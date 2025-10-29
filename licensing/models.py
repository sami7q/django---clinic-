from django.db import models
from django.utils import timezone

class UsedLicense(models.Model):
    signature = models.CharField(max_length=128, unique=True)
    used_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"USED {self.signature[:10]}..."

class LicenseKey(models.Model):
    # تمثيل الترخيص (حزمة الترخيص كما يولده المولد)
    device_id = models.CharField(max_length=255, blank=True, null=True)  # package id
    expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    signature = models.CharField(max_length=128, unique=True)
    allowed_devices = models.IntegerField(default=1)   # العدد المسموح
    remaining_devices = models.IntegerField(default=1) # العدد المتبقي (يتناقص عند التفعيل)

    def __str__(self):
        return self.device_id or "Offline License"

    @property
    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at

class RegisteredDevice(models.Model):
    """
    الأجهزة المسجلة ضمن ترخيص معيّن. نربطها بـ LicenseKey عبر signature.
    نخزن معرّف الجهاز الحقيقي (مثال: هاش من machine id) وتاريخ التفعيل.
    """
    license = models.ForeignKey(LicenseKey, on_delete=models.CASCADE, related_name="registered_devices")
    machine_hash = models.CharField(max_length=255)  # تخزين هاش معرف الجهاز
    activated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("license", "machine_hash")

    def __str__(self):
        return f"{self.machine_hash[:8]}... for {self.license}"
