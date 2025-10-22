from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=64)
    ip = models.GenericIPAddressField(null=True, blank=True)
    ua = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
