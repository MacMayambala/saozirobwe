from django.db import models
from django.contrib.auth.models import User  # Using built-in User model
from django.db import models
from django.conf import settings
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from django.db import models
from django.core.exceptions import ValidationError
from base64 import b32decode
from django.conf import settings

def validate_base32(value):
    if value:
        try:
            b32decode(value, casefold=False)
        except Exception:
            raise ValidationError("Invalid base32 string.")

class TwoFactorAuth(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    secret_key = models.CharField(max_length=100, blank=True, null=True, validators=[validate_base32])
    email_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    mfa_enabled = models.BooleanField(default=False)
    auth_method = models.CharField(max_length=20, blank=True, null=True)  # Track method

    def clean(self):
        if self.secret_key:
            validate_base32(self.secret_key)



class Module(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class UserModuleAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Linking to built-in User
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'module')  # Prevent duplicate user-module entries

    def __str__(self):
        return f"{self.user.username} - {self.module.name}"
    



from django.db import models
from django.contrib.auth.models import User

class UserSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='active_session')
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.session_key}"
    



    



