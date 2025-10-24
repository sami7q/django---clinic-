from django.db import models

class Patient(models.Model):
    GENDER_CHOICES = [
        ('ذكر', 'ذكر'),
        ('أنثى', 'أنثى'),
    ]

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='ذكر')  # 🧩 تمت الإضافة هنا
    phone = models.CharField(max_length=20, blank=True, null=True)  # 📞 رقم الهاتف
    diagnosis = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.gender})"
