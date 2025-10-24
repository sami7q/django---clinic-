from django.db import models
from django.utils import timezone
from patients.models import Patient
from appointments.models import Appointment
from django.contrib.auth.models import User


# 💰 نموذج الفواتير
class Invoice(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'نقدًا'),
        ('card', 'بطاقة'),
        ('transfer', 'تحويل'),
    ]
    STATUS_CHOICES = [
        ('مدفوعة', 'مدفوعة'),
        ('غير مدفوعة', 'غير مدفوعة'),
        ('مؤجلة', 'مؤجلة'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    clinic_name = models.CharField(max_length=150, default="عيادة سامي الطبية")

    invoice_number = models.PositiveIntegerField(default=0, editable=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='غير مدفوعة')
    notes = models.TextField(blank=True, null=True)

    date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """توليد رقم فاتورة يبدأ من 1 كل يوم جديد"""
        if not self.invoice_number:
            today = timezone.localdate()
            last_invoice = Invoice.objects.filter(date__date=today).order_by('-invoice_number').first()
            self.invoice_number = (last_invoice.invoice_number + 1) if last_invoice else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"فاتورة {self.invoice_number} - {self.patient.name}"

    @property
    def remaining(self):
        return max(self.total_amount - self.paid_amount, 0)


# 🧾 عناصر الفاتورة
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} ({self.total})"


# 💸 نموذج النفقات
class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("رواتب", "رواتب"),
        ("فواتير", "فواتير"),
        ("أجار", "أجار"),
        ("مستلزمات", "مستلزمات"),
        ("أخرى", "أخرى"),
    ]

    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    notes = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} - {self.amount} د.ع"
