from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'phone', 'diagnosis', 'created_at']
    search_fields = ['name', 'phone', 'diagnosis']
    list_filter = ['created_at']
