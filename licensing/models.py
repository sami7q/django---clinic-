from django.db import models
from django.utils import timezone
from datetime import timedelta

class LicenseKey(models.Model):
    code = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=False)
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} ({'مفعل' if self.is_active else 'منتهي'})"

    def is_valid(self):
        """يتحقق إن كانت الرخصة ما تزال صالحة."""
        if not self.is_active or not self.expires_at:
            return False
        return timezone.now() < self.expires_at

    def activate(self, code):
        """تفعيل الرخصة لمدة 30 يومًا."""
        self.code = code
        self.is_active = True
        self.activated_at = timezone.now()
        self.expires_at = timezone.now() + timedelta(days=30)
        self.save()
