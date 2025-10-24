from django.shortcuts import render
from django.db.models import Sum
from patients.models import Patient
from appointments.models import Appointment
from invoices.models import Invoice
from django.contrib.auth.models import User
from datetime import date, timedelta

def home(request):
    # 🔹 إحصائيات عامة
    total_patients = Patient.objects.count()
    today_patients = Patient.objects.filter(created_at__date=date.today()).count()
    total_appointments = Appointment.objects.count()
    recent_appointments = Appointment.objects.filter(date__gte=date.today() - timedelta(days=1)).count()
    
    # 🔹 الفواتير والإيرادات
    total_invoices = Invoice.objects.aggregate(total=Sum("total_amount"))['total'] or 0
    this_week_invoices = Invoice.objects.filter(
        date__gte=date.today() - timedelta(days=7)
    ).aggregate(total=Sum("total_amount"))['total'] or 0

    # 🔹 المستخدمين والمرضى الجدد
    users_count = User.objects.count()
    recent_patients = Patient.objects.order_by('-created_at')[:5]

    context = {
        "total_patients": total_patients,
        "today_patients": today_patients,
        "total_appointments": total_appointments,
        "recent_appointments": recent_appointments,
        "total_invoices": total_invoices,
        "this_week_invoices": this_week_invoices,
        "users_count": users_count,
        "recent_patients": recent_patients,
    }
    return render(request, "dashboard/home.html", context)
