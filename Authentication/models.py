from django.db import models
from django.contrib.auth.models import User

class OTPCode(models.Model):
    class CodeStatus(models.IntegerChoices):
        NOT_VERIFIED = 0
        VERIFIED = 1
        FAILED = 2
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=100)
    code = models.CharField(max_length=6)
    secret_key = models.CharField(max_length=32)
    status = models.IntegerField(choices=CodeStatus.choices, default=CodeStatus.NOT_VERIFIED)
    expiry_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
