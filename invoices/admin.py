from django.contrib import admin
from .models import Invoice, Expense, Income


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'consultation_fee', 'paid', 'date')
    list_filter = ('paid', 'date')
    search_fields = ('patient__name',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'date')
    search_fields = ('title',)


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'source', 'date')
    search_fields = ('title', 'source')
