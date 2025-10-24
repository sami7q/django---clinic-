from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'مدير النظام'),
        ('doctor', 'طبيب'),
        ('reception', 'استقبال'),
        ('accountant', 'محاسب'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reception')

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
