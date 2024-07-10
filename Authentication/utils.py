import random, string, os
from django.contrib.auth.models import User
from .models import OTPCode
from celery import shared_task
from django.core.mail import send_mail

def generate_username():
    while True:
        username = 'ecommerce' + ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=16))
        if User.objects.filter(username__iexact=username).exists():
            continue
        else:
            break
    return username

def generate_otp():
    while True:
        code = ''.join(random.choices('0123456789', k=6))
        secret_key = ''.join(random.choices(string.ascii_letters, k=16))
        if OTPCode.objects.filter(code=code, secret_key=secret_key).exists():
            continue
        else:
            break
    return code, secret_key

@shared_task
def send_otp(otp, receiver):
    subject = 'OTP Verification'
    message = f'Dear Customer, this is the OTP {otp} for your login'
    from_email = os.getenv('DEFAULT_FROM_EMAIL')
    recipient_list = [receiver]

    send_mail(subject, message, from_email, recipient_list)
    return "OTP sent"