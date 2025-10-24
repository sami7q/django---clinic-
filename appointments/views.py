from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import FieldDoesNotExist
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
from collections import defaultdict
import json
from .models import Appointment
from .forms import AppointmentForm
from patients.models import Patient


# ✅ قائمة المواعيد القادمة فقط
def appointments_list(request):
    """📅 عرض المواعيد القادمة فقط (المستقبلية فقط)"""
    now = timezone.localtime()
    current_date = now.date()
    current_time = now.time()

    appointments = Appointment.objects.filter(
        date__gt=current_date
    ) | Appointment.objects.filter(
        date=current_date, time__gte=current_time
    )
    appointments = appointments.order_by('date', 'time')

    appointments_json = json.dumps([
        {
            "id": a.id,
            "patient": str(a.patient),
            "phone": getattr(a.patient, "phone", ""),
            "date": a.date.strftime("%Y-%m-%d"),
            "time": a.time.strftime("%H:%M"),
            "reason": a.reason,
            "status": a.status,
            "edit_url": reverse("appointments:edit", args=[a.id]),
            "delete_url": reverse("appointments:delete", args=[a.id]),
        }
        for a in appointments
    ], ensure_ascii=False)

    return render(request, "appointments/list.html", {
        "appointments": appointments,
        "appointments_json": appointments_json,
        "show_all": False
    })


# ✅ جميع المواعيد (منتهية + قادمة)
def appointments_all(request):
    """📜 عرض جميع المواعيد (القديمة + القادمة)"""
    appointments = Appointment.objects.all().order_by("-date", "-time")

    appointments_json = json.dumps([
        {
            "id": a.id,
            "patient": str(a.patient),
            "phone": getattr(a.patient, "phone", ""),
            "date": a.date.strftime("%Y-%m-%d"),
            "time": a.time.strftime("%H:%M"),
            "reason": a.reason,
            "status": a.status,
            "edit_url": reverse("appointments:edit", args=[a.id]),
            "delete_url": reverse("appointments:delete", args=[a.id]),
        }
        for a in appointments
    ], ensure_ascii=False)

    return render(request, "appointments/list.html", {
        "appointments": appointments,
        "appointments_json": appointments_json,
        "show_all": True
    })


# ✅ إنشاء موعد جديد
def appointment_create(request):
    """➕ إنشاء موعد جديد"""
    form = AppointmentForm(request.POST or None)

    # المرضى (نشطين أو جميعًا)
    try:
        Patient._meta.get_field("is_active")
        patients_active = Patient.objects.filter(is_active=True).order_by("name")
        patients_archived = Patient.objects.filter(is_active=False).order_by("name")
        patients = None
    except FieldDoesNotExist:
        patients = Patient.objects.all().order_by("name")
        patients_active = patients_archived = None

    # الأوقات المحجوزة
    booked_map = defaultdict(list)
    for appt in Appointment.objects.all().only("date", "time"):
        date_str = appt.date.strftime("%Y-%m-%d")
        time_str = appt.time.strftime("%H:%M")
        booked_map[date_str].append(time_str)

    booked_slots_json = json.dumps(booked_map, ensure_ascii=False)

    if form.is_valid():
        form.save()
        return redirect("appointments:list")

    context = {
        "form": form,
        "patients_active": patients_active,
        "patients_archived": patients_archived,
        "patients": patients,
        "booked_slots_json": booked_slots_json,
    }
    return render(request, "appointments/create.html", context)


# ✅ تعديل موعد
def appointment_edit(request, pk):
    """✏️ تعديل موعد"""
    appointment = get_object_or_404(Appointment, pk=pk)
    form = AppointmentForm(request.POST or None, instance=appointment)

    # 🧩 الأوقات المحجوزة لجميع الأيام
    booked_map = defaultdict(list)
    for appt in Appointment.objects.all().only("date", "time"):
        date_str = appt.date.strftime("%Y-%m-%d")
        time_str = appt.time.strftime("%H:%M")
        booked_map[date_str].append(time_str)

    # ⚙️ استبعاد اليوم السابق بالكامل بدقة (يظهر فقط اليوم وما بعده)
    today = timezone.localdate()
    booked_map = {
        d: times for d, times in booked_map.items()
        if d >= today.strftime("%Y-%m-%d")
    }

    booked_slots_json = json.dumps(booked_map, ensure_ascii=False)

    if form.is_valid():
        form.save()
        return redirect("appointments:list")

    context = {
        "form": form,
        "appointment": appointment,
        "booked_slots_json": booked_slots_json,
        "current_date": appointment.date.strftime("%Y-%m-%d"),
        "current_time": appointment.time.strftime("%H:%M"),
    }
    return render(request, "appointments/update.html", context)


# ✅ حذف موعد
def appointment_delete(request, pk):
    """🗑️ حذف موعد"""
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        appointment.delete()
        return redirect("appointments:list")
    return render(request, "appointments/delete.html", {"appointment": appointment})


# ✅ بحث المرضى
def patient_search(request):
    """🔍 بحث سريع عن المرضى"""
    query = request.GET.get("q", "")
    results = []
    if query:
        patients = Patient.objects.filter(name__icontains=query)[:10]
        results = [{"id": p.id, "name": p.name, "phone": p.phone} for p in patients]
    return JsonResponse(results, safe=False)
