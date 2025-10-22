from django.db import models
from django.utils import timezone
from patients.models import Patient


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'قيد الانتظار'),
        ('completed', 'تمت الزيارة'),
        ('cancelled', 'ألغيت'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name="المريض"
    )
    date = models.DateField(default=timezone.now, verbose_name="تاريخ الموعد")
    time = models.TimeField(default=timezone.now, verbose_name="الوقت")
    reason = models.TextField(blank=True, null=True, verbose_name="سبب الزيارة")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name="الحالة"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "موعد"
        verbose_name_plural = "المواعيد"
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.patient.name} - {self.date} {self.time} ({self.get_status_display()})"
