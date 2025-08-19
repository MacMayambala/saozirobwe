from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    url = models.CharField(max_length=255, default='/unknown/')  # Default value added
    method = models.CharField(max_length=10, default='GET')  # Default value added
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Allow null
    timestamp = models.DateTimeField(auto_now_add=True)
   
    details = models.TextField(blank=True, null=True) 
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
