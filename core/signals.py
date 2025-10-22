from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from .models import ActivityLog

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    ActivityLog.objects.create(
        user=user,
        action="login",
        ip=request.META.get("REMOTE_ADDR"),
        ua=request.META.get("HTTP_USER_AGENT", ""),
        created_at=timezone.now()
    )
