# invoices/models.py
from django.db import models
from patients.models import Patient  # أو من core.models إذا كان عندك الموديل هناك


class Invoice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="invoices")
    date = models.DateTimeField(auto_now_add=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"فاتورة {self.id} - {self.patient.name}"


class Expense(models.Model):
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.amount} IQD"


class Income(models.Model):
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=255, default="كشفية")
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.amount} IQD"
