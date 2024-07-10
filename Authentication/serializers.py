from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OTPCode

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'is_staff')


class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPCode
        fields = ('email', 'code', 'secret_key')