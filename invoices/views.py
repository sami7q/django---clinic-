from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import Invoice, Expense, Income
from patients.models import Patient


# 🧾 عرض قائمة الفواتير + الإحصائيات
def invoice_list(request):
    invoices = Invoice.objects.select_related('patient').order_by('-date')

    # إحصائيات سريعة
    total_income = Invoice.objects.aggregate(total=Sum("consultation_fee"))["total"] or 0
    unpaid_count = Invoice.objects.filter(paid=False).count()
    invoice_count = invoices.count()

    context = {
        "invoices": invoices,
        "total_income": total_income,
        "unpaid_count": unpaid_count,
        "invoice_count": invoice_count,
    }
    return render(request, "invoices/list.html", context)


# ➕ إنشاء فاتورة جديدة
def invoice_create(request):
    patients = Patient.objects.all()

    if request.method == "POST":
        patient_id = request.POST.get("patient")
        consultation_fee = request.POST.get("consultation_fee")
        notes = request.POST.get("notes")

        patient = get_object_or_404(Patient, id=patient_id)
        invoice = Invoice.objects.create(
            patient=patient,
            consultation_fee=consultation_fee,
            notes=notes,
        )

        # إنشاء سجل دخل تلقائي عند كل كشفية
        Income.objects.create(
            title=f"كشفية {patient.name}",
            amount=consultation_fee,
            source="كشفية",
        )

        return redirect("invoices:list")

    return render(request, "invoices/create.html", {"patients": patients})


# ✏️ تعديل فاتورة موجودة
def invoice_update(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    patients = Patient.objects.all()

    if request.method == "POST":
        invoice.patient_id = request.POST.get("patient")
        invoice.consultation_fee = request.POST.get("consultation_fee")
        invoice.notes = request.POST.get("notes")
        invoice.paid = 'paid' in request.POST
        invoice.save()
        return redirect("invoices:list")

    return render(request, "invoices/update.html", {"invoice": invoice, "patients": patients})


# ❌ حذف فاتورة
def invoice_delete(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    invoice.delete()
    return redirect("invoices:list")


# 📊 ملخص مالي (الدخل والنفقات)
def financial_summary(request):
    total_income = Income.objects.aggregate(Sum("amount"))["amount__sum"] or 0
    total_expenses = Expense.objects.aggregate(Sum("amount"))["amount__sum"] or 0
    net_profit = total_income - total_expenses

    return render(request, "invoices/summary.html", {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "incomes": Income.objects.all().order_by('-date'),
        "expenses": Expense.objects.all().order_by('-date'),
    })
