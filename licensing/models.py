from django.db import models
from django.utils import timezone
import uuid

def generate_license_key():
    return uuid.uuid4().hex

class LicenseKey(models.Model):
    key = models.CharField(max_length=64, unique=True, default=generate_license_key)
    issued_to = models.CharField(max_length=255, blank=True, default="")
    issued_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)

    def is_valid(self):
        return (not self.is_revoked) and (self.expires_at >= timezone.now())
