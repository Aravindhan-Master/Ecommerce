from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponseRedirect
import json, random
import google_auth_oauthlib
from googleapiclient.discovery import build
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .utils import generate_username, generate_otp, send_otp
from .serializers import UserSerializer, OTPSerializer
from .models import OTPCode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from products.models import Product
from ecommerce.celery import app
import datetime

GOOGLE_OAUTH_CONF_FILE_PATH = 'google_auth_conf.json'

def create_user(data, is_admin=False):
    data = json.loads(data)
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({"error": "An account with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)

    user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_admin,
        )
    
    user.set_password(password)
    user.save()
    token = Token.objects.create(user=user)
    response = {
        "message": "User created successfully",
        "token": token.key
    }
    return Response(response, status=status.HTTP_201_CREATED)

class ScheduledTaskView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        tasks = app.conf.beat_schedule
        response = {
            'tasks': tasks
        }
        return Response(response, status=status.HTTP_200_OK)

class UserSignUpView(APIView):
    def get(self, request):
        return Response({'message': 'User Register View'})
    
    def post(self, request):
        user = create_user(request.body, is_admin=False)
        return user

class AdminSignUpView(APIView):
    def get(self, request):
        return Response({'message': 'Admin Register View'})
    
    def post(self, request):
        user = create_user(request.body, is_admin=True)
        return user

class LoginView(APIView):
    def get(self, request):
        return Response({'message': 'Login View'})
    
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            token, create = Token.objects.get_or_create(user=user)
            response = {
                'message': "Login Successful",
                'token': token.key
            }
            return Response(response, status=status.HTTP_202_ACCEPTED)
        
        return Response({'response': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
class GoogleOAuthLogin(View):
    def get(self, request):
        return render(request, 'Authentication/login.html')
    
    def post(self, request):
        with open(GOOGLE_OAUTH_CONF_FILE_PATH, "r") as config_file:
            google_oauth_config = json.load(config_file)

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            GOOGLE_OAUTH_CONF_FILE_PATH,
            scopes=["https://www.googleapis.com/auth/userinfo.email",
                    "https://www.googleapis.com/auth/userinfo.profile",
                    "openid"])
        
        flow.redirect_uri = google_oauth_config["web"]["redirect_uris"][0]

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true')
        
        request.session['state'] = state
        return HttpResponseRedirect(authorization_url)

class GoogleOAuthCallback(APIView):
    def get(self, request):
        with open(GOOGLE_OAUTH_CONF_FILE_PATH, "r") as file:
            google_oauth_config = json.load(file)
        
        state = request.GET.get("state")
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            GOOGLE_OAUTH_CONF_FILE_PATH,
            scopes=["https://www.googleapis.com/auth/userinfo.email",
                    "https://www.googleapis.com/auth/userinfo.profile",
                    "openid"],
            state=state)
        
        flow.redirect_uri = google_oauth_config["web"]["redirect_uris"][0]
        flow.fetch_token(code = request.GET["code"])

        oauth_build = build("oauth2", "v2", credentials=flow.credentials)
        user_info = oauth_build.userinfo().get().execute()
        user = User.objects.filter(email=user_info['email'])
        if user:
            token, create = Token.objects.get_or_create(user=user.first())
            response = {
                'message': "Login Successful",
                'token': token.key
            }
            return Response(response, status=status.HTTP_202_ACCEPTED)
            
        else:
            request.session['user_details'] = user_info 
            new_user = User(
                            username=generate_username(),
                            is_superuser=False,
                            first_name=user_info['given_name'],
                            last_name=user_info['family_name'],
                            email=user_info['email'],
                            is_staff=False
                            )
            password="".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=16))
            new_user.set_password(password)
            new_user.save()

            token = Token.objects.create(user=new_user)
            response = {
                "message": "Login successful",
                "token": token.key
            }
            return Response(response, status=status.HTTP_201_CREATED)
        
class OTPLoginView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({"message": "User already logged in"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'OTP View'}, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.is_authenticated:
            return Response({"message": "User already logged in"}, status=status.HTTP_400_BAD_REQUEST)
        data = json.loads(request.body)
        email = data.get('email')
        user = User.objects.filter(email=email)
        if not user:
            return Response({'error': 'No such email is associated with this application'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = user.first()
        code, secret_key = generate_otp()
        five_minutes_later = datetime.datetime.now() + datetime.timedelta(minutes=5)
        otp_obj = OTPCode.objects.create(
                    email=email,
                    user = user,
                    code = code,
                    secret_key = secret_key,
                    expiry_time = five_minutes_later
                )
        send_otp.delay(code, email)
        serializer = OTPSerializer(otp_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class OTPVerifyView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            return Response({"message": "User already logged in"}, status=status.HTTP_400_BAD_REQUEST)
        data = json.loads(request.body)
        code = data.get('code')
        secret_key = data.get('secret_key')
        code_objs = OTPCode.objects.filter(code=code, secret_key=secret_key)
        if not code_objs:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        
        code_obj = code_objs.first()
        if code_obj.expiry_time.replace(tzinfo=None) < datetime.datetime.now():
            code_obj.status = OTPCode.CodeStatus.FAILED
            code_obj.save()
            return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        code_obj.status = OTPCode.CodeStatus.VERIFIED
        code_obj.save()

        token = Token.objects.create(user=code_obj.user)
        response = {
            'token': token.key
        }
        return Response(response, status=status.HTTP_200_OK)

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.get(user=request.user).delete()
        return Response({'message': 'User logged out'}, status=status.HTTP_200_OK)
