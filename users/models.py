# users/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
from base64 import b32decode

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
    auth_method = models.CharField(max_length=20, blank=True, null=True)

    def clean(self):
        if self.secret_key:
            validate_base32(self.secret_key)

class Module(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class UserModuleAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'module')

    def __str__(self):
        return f"{self.user.username} - {self.module.name}"

class UserSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='active_session')
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.session_key}"
#######################################################################################
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class FailedLoginAttempt(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="failed_login")
    attempts = models.PositiveIntegerField(default=0)
    last_attempt = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.attempts} failed attempts"


# users/models.py
from django.conf import settings
from django.db import models

class PasswordHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    password = models.CharField(max_length=128)  # Store hashed password
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Password Histories"
