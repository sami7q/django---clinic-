from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from patients.models import Patient
from appointments.models import Appointment
from invoices.models import Invoice

def home(request):
    """الصفحة الرئيسية للوحة التحكم"""

    # 🕒 الوقت والتاريخ الحالي
    now = timezone.localtime()
    current_date = now.date()
    current_time = now.time()

    # 📊 الإحصائيات العامة
    total_patients = Patient.objects.count()
    today_patients = Patient.objects.filter(created_at__date=current_date).count()

    total_appointments = Appointment.objects.count()
    total_invoices = Invoice.objects.aggregate(total=Sum("total_amount"))["total"] or 0
    week_invoices = (
        Invoice.objects.filter(date__gte=current_date - timedelta(days=7))
        .aggregate(total=Sum("total_amount"))["total"]
        or 0
    )
    users_count = User.objects.count()

    # 📅 المواعيد القادمة فقط (نفس منطقك الذكي)
    upcoming_appointments = Appointment.objects.filter(
        date__gt=current_date
    ) | Appointment.objects.filter(
        date=current_date, time__gte=current_time
    )
    upcoming_appointments = upcoming_appointments.order_by("date", "time")[:5]

    # 🧾 أحدث الأنشطة (آخر 5 مرضى تمت إضافتهم)
    recent_patients = Patient.objects.order_by("-created_at")[:5]
    recent_activities = [
        {"icon": "👤", "text": f"تمت إضافة المريض {p.name}", "date": p.created_at}
        for p in recent_patients
    ]

    context = {
        "total_patients": total_patients,
        "today_patients": today_patients,
        "total_appointments": total_appointments,
        "total_invoices": total_invoices,
        "week_invoices": week_invoices,
        "users_count": users_count,
        "upcoming_appointments": upcoming_appointments,
        "recent_activities": recent_activities,
    }

    return render(request, "dashboard/home.html", context)
