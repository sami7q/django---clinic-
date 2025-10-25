from django.shortcuts import render, redirect, get_object_or_404
from django.utils.dateparse import parse_date, parse_time
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


# ✅ جميع المواعيد (القديمة + القادمة)
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


# ✅ إنشاء موعد جديد (مصحح)
def appointment_create(request):
    """➕ إنشاء موعد جديد"""
    form = AppointmentForm(request.POST or None)

    # 🧩 الأوقات المحجوزة
    booked_map = defaultdict(list)
    for appt in Appointment.objects.all().only("date", "time"):
        date_str = appt.date.strftime("%Y-%m-%d")
        time_str = appt.time.strftime("%H:%M")
        booked_map[date_str].append(time_str)
    booked_slots_json = json.dumps(booked_map, ensure_ascii=False)

    if request.method == "POST":
        print("🧠 POST DATA:", request.POST.dict())

        try:
            # نحصل على القيم يدويًا
            patient_id = request.POST.get("patient")
            appointment_date = parse_date(request.POST.get("date"))
            appointment_time = parse_time(request.POST.get("time"))
            reason = request.POST.get("reason", "")
            status = request.POST.get("status", "لم يحن الموعد")

            if not (patient_id and appointment_date and appointment_time):
                print("⚠️ Missing required fields:", patient_id, appointment_date, appointment_time)
                return render(request, "appointments/create.html", {
                    "form": form,
                    "booked_slots_json": booked_slots_json,
                    "error": "يجب تحديد المريض والتاريخ والوقت."
                })

            # حفظ الموعد
            patient = Patient.objects.get(pk=patient_id)
            Appointment.objects.create(
                patient=patient,
                date=appointment_date,
                time=appointment_time,
                reason=reason,
                status=status,
            )
            print("✅ Appointment saved successfully.")
            return redirect("appointments:list")

        except Exception as e:
            print("❌ Error while saving appointment:", e)
            return render(request, "appointments/create.html", {
                "form": form,
                "booked_slots_json": booked_slots_json,
                "error": "حدث خطأ أثناء حفظ الموعد."
            })

    context = {
        "form": form,
        "booked_slots_json": booked_slots_json,
    }
    return render(request, "appointments/create.html", context)


# ✅ تعديل موعد
def appointment_edit(request, pk):
    """✏️ تعديل موعد"""
    appointment = get_object_or_404(Appointment, pk=pk)
    form = AppointmentForm(request.POST or None, instance=appointment)

    # 🧩 الأوقات المحجوزة
    booked_map = defaultdict(list)
    for appt in Appointment.objects.all().only("date", "time"):
        date_str = appt.date.strftime("%Y-%m-%d")
        time_str = appt.time.strftime("%H:%M")
        booked_map[date_str].append(time_str)

    today = timezone.localdate()
    booked_map = {
        d: times for d, times in booked_map.items()
        if d >= today.strftime("%Y-%m-%d")
    }
    booked_slots_json = json.dumps(booked_map, ensure_ascii=False)

    if request.method == "POST":
        try:
            patient_id = request.POST.get("patient")
            appointment_date = parse_date(request.POST.get("date"))
            appointment_time = parse_time(request.POST.get("time"))
            reason = request.POST.get("reason", "")
            status = request.POST.get("status", "لم يحن الموعد")

            if patient_id:
                appointment.patient = Patient.objects.get(pk=patient_id)
            appointment.date = appointment_date
            appointment.time = appointment_time
            appointment.reason = reason
            appointment.status = status
            appointment.save()

            print("✅ Appointment updated successfully.")
            return redirect("appointments:list")

        except Exception as e:
            print("❌ Error updating appointment:", e)

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
        print("🗑️ Appointment deleted:", pk)
        return redirect("appointments:list")
    return render(request, "appointments/delete.html", {"appointment": appointment})


# ✅ بحث المرضى (للبحث الذكي عند إنشاء الموعد)
def patient_search(request):
    """🔍 بحث سريع عن المرضى"""
    query = request.GET.get("q", "")
    results = []
    if query:
        patients = Patient.objects.filter(name__icontains=query)[:10]
        results = [{"id": p.id, "name": p.name, "phone": p.phone} for p in patients]
    return JsonResponse(results, safe=False)
