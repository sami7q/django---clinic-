from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from django.utils import timezone
from django.http import JsonResponse, Http404
from django.contrib import messages
from .models import Invoice, InvoiceItem, Expense
from patients.models import Patient


# 🧾 الصفحة الرئيسية - فواتير اليوم
def invoice_list(request):
    today = timezone.localdate()
    invoices = Invoice.objects.filter(date__date=today).select_related("patient", "doctor").order_by("-date")

    context = {
        "invoices": invoices,
        "filter_label": "فواتير اليوم",
        "total_revenue": Invoice.objects.aggregate(total=Sum("total_amount"))["total"] or 0,
        "total_expenses": Expense.objects.aggregate(total=Sum("amount"))["total"] or 0,
        "invoice_count": invoices.count(),
    }
    return render(request, "invoices/list.html", context)


# 🔎 فلترة الفواتير (اليوم / الأمس / الكل)
def invoice_filter(request, period):
    today = timezone.localdate()
    invoices = Invoice.objects.none()
    label = ""

    if period == "today":
        invoices = Invoice.objects.filter(date__date=today)
        label = "فواتير اليوم"
    elif period == "yesterday":
        invoices = Invoice.objects.filter(date__date=today - timedelta(days=1))
        label = "فواتير الأمس"
    elif period == "all":
        invoices = Invoice.objects.all()
        label = "جميع الفواتير"

    invoices = invoices.select_related("patient", "doctor").order_by("-date")

    context = {
        "invoices": invoices,
        "filter_label": label,
        "total_revenue": Invoice.objects.aggregate(total=Sum("total_amount"))["total"] or 0,
        "total_expenses": Expense.objects.aggregate(total=Sum("amount"))["total"] or 0,
        "invoice_count": invoices.count(),
    }
    return render(request, "invoices/list.html", context)


# ➕ إنشاء فاتورة جديدة
def invoice_create(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient")
        if not patient_id:
            messages.error(request, "يجب اختيار المريض قبل إنشاء الفاتورة.")
            return render(request, "invoices/create.html")

        patient = get_object_or_404(Patient, id=patient_id)
        discount = float(request.POST.get("discount") or 0)
        payment_method = request.POST.get("payment_method", "cash")
        notes = request.POST.get("notes", "")
        doctor = request.user if request.user.is_authenticated else None

        invoice = Invoice.objects.create(
            patient=patient,
            doctor=doctor,
            discount=discount,
            payment_method=payment_method,
            notes=notes,
            date=timezone.now(),
            status="مدفوعة" if payment_method else "غير مدفوعة",
        )

        InvoiceItem.objects.create(
            invoice=invoice,
            description="مراجعة عيادة",
            quantity=1,
            unit_price=25000,
        )

        invoice.total_amount = 25000
        invoice.paid_amount = 25000 - discount
        invoice.save()

        return redirect("invoices:print", pk=invoice.pk)

    return render(request, "invoices/create.html")


# ✏️ تعديل فاتورة
def invoice_update(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = invoice.items.all()

    if request.method == "POST":
        invoice.discount = float(request.POST.get("discount") or 0)
        invoice.payment_method = request.POST.get("payment_method", invoice.payment_method)
        invoice.notes = request.POST.get("notes", "")
        invoice.status = "مدفوعة" if invoice.paid_amount >= (invoice.total_amount - invoice.discount) else "غير مدفوعة"
        invoice.save()
        messages.success(request, "تم تحديث الفاتورة بنجاح.")
        return redirect("invoices:list")

    return render(request, "invoices/update.html", {"invoice": invoice, "items": items})


# ❌ حذف فاتورة
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.delete()
    messages.warning(request, "تم حذف الفاتورة بنجاح.")
    return redirect("invoices:list")


# 🖨️ طباعة فاتورة معينة
def invoice_print(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = InvoiceItem.objects.filter(invoice=invoice)
    return render(request, "invoices/print.html", {"invoice": invoice, "items": items})


# 🖨️ طباعة آخر فاتورة
def print_latest_invoice(request):
    latest_invoice = Invoice.objects.order_by("-id").first()
    if not latest_invoice:
        raise Http404("لا توجد فواتير للطباعة.")
    return redirect("invoices:print", pk=latest_invoice.pk)


# 💸 إنشاء نفقة جديدة
def expense_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        amount = request.POST.get("amount")
        category = request.POST.get("category")
        notes = request.POST.get("notes", "")

        if not title or not amount or not category:
            messages.error(request, "الرجاء تعبئة جميع الحقول المطلوبة.")
            return render(request, "invoices/expense_create.html")

        Expense.objects.create(
            title=title,
            amount=amount,
            category=category,
            notes=notes,
            date=timezone.now()
        )

        messages.success(request, f"تم حفظ النفقة ({title}) بقيمة {amount} د.ع.")
        return redirect("invoices:expense_list")

    return render(request, "invoices/expense_create.html")


# 📊 عرض النفقات (اليوم / الأمس / الكل)
def expense_list(request):
    today = timezone.localdate()
    filter_type = request.GET.get("filter", "today")

    if filter_type == "yesterday":
        expenses = Expense.objects.filter(date__date=today - timedelta(days=1))
        label = "نفقات الأمس"
    elif filter_type == "all":
        expenses = Expense.objects.all().order_by("-date")
        label = "جميع النفقات"
    else:
        expenses = Expense.objects.filter(date__date=today)
        label = "نفقات اليوم"

    total = expenses.aggregate(total=Sum("amount"))["total"] or 0

    context = {
        "expenses": expenses,
        "label": label,
        "total": total,
    }
    return render(request, "invoices/expense_list.html", context)


# 🔍 بحث ذكي عن المريض (HTMX)
def patient_search(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse([], safe=False)
    patients = Patient.objects.filter(name__icontains=query)[:10]
    results = [{"id": p.id, "name": p.name, "phone": p.phone or ""} for p in patients]
    return JsonResponse(results, safe=False)
