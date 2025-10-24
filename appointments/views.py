from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import FieldDoesNotExist
from django.utils import timezone
from collections import defaultdict
from datetime import datetime
import json
from .models import Appointment
from .forms import AppointmentForm
from patients.models import Patient


# ✅ قائمة المواعيد القادمة فقط
def appointments_list(request):
    """📅 عرض المواعيد القادمة فقط (المستقبلية فقط)"""
    now = timezone.localtime()  # الوقت والتاريخ الحالي من النظام
    current_date = now.date()
    current_time = now.time()

    # جلب المواعيد التي لم يأتِ وقتها بعد
    appointments = Appointment.objects.filter(
        date__gt=current_date
    ) | Appointment.objects.filter(
        date=current_date, time__gte=current_time
    )
    appointments = appointments.order_by('date', 'time')

    # تجهيز البيانات للواجهة (Alpine.js)
    appointments_json = json.dumps([
        {
            "id": a.id,
            "patient": str(a.patient),
            "phone": getattr(a.patient, "phone", ""),
            "date": a.date.strftime("%Y-%m-%d"),
            "time": a.time.strftime("%H:%M"),
            "reason": a.reason,
            "status": a.status,
            "edit_url": f"/appointments/{a.id}/update/",
            "delete_url": f"/appointments/{a.id}/delete/"
        }
        for a in appointments
    ], ensure_ascii=False)

    return render(request, 'appointments/list.html', {
        'appointments': appointments,
        'appointments_json': appointments_json,
        'show_all': False
    })


# ✅ جميع المواعيد (منتهية + قادمة)
def appointments_all(request):
    """📜 عرض جميع المواعيد (القديمة + القادمة)"""
    appointments = Appointment.objects.all().order_by('-date', '-time')

    appointments_json = json.dumps([
        {
            "id": a.id,
            "patient": str(a.patient),
            "phone": getattr(a.patient, "phone", ""),
            "date": a.date.strftime("%Y-%m-%d"),
            "time": a.time.strftime("%H:%M"),
            "reason": a.reason,
            "status": a.status,
            "edit_url": f"/appointments/{a.id}/update/",
            "delete_url": f"/appointments/{a.id}/delete/"
        }
        for a in appointments
    ], ensure_ascii=False)

    return render(request, 'appointments/list.html', {
        'appointments': appointments,
        'appointments_json': appointments_json,
        'show_all': True
    })


# ✅ إنشاء موعد جديد
def appointment_create(request):
    """➕ إنشاء موعد جديد"""
    form = AppointmentForm(request.POST or None)

    # المرضى (نشطين أو جميعًا)
    patients_active = None
    patients_archived = None
    patients = None
    try:
        Patient._meta.get_field('is_active')
        patients_active = Patient.objects.filter(is_active=True).order_by('name')
        patients_archived = Patient.objects.filter(is_active=False).order_by('name')
    except FieldDoesNotExist:
        patients = Patient.objects.all().order_by('name')

    # الأوقات المحجوزة لكل يوم (لتفادي التعارض)
    booked_map = defaultdict(list)
    for appt in Appointment.objects.all().only('date', 'time'):
        date_str = appt.date.strftime('%Y-%m-%d')
        time_str = appt.time.strftime('%H:%M')
        booked_map[date_str].append(time_str)

    booked_slots_json = json.dumps(booked_map, ensure_ascii=False)

    if form.is_valid():
        form.save()
        return redirect('appointments:list')

    context = {
        'form': form,
        'patients_active': patients_active,
        'patients_archived': patients_archived,
        'patients': patients,
        'booked_slots_json': booked_slots_json,
    }
    return render(request, 'appointments/create.html', context)


# ✅ تعديل موعد
def appointment_update(request, id):
    """✏️ تعديل موعد"""
    appointment = get_object_or_404(Appointment, id=id)
    form = AppointmentForm(request.POST or None, instance=appointment)
    if form.is_valid():
        form.save()
        return redirect('appointments:list')
    return render(request, 'appointments/update.html', {'form': form})


# ✅ حذف موعد
def appointment_delete(request, id):
    """🗑️ حذف موعد"""
    appointment = get_object_or_404(Appointment, id=id)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointments:list')
    return render(request, 'appointments/delete.html', {'appointment': appointment})

def patient_search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        patients = Patient.objects.filter(name__icontains=query)[:10]
        results = [{"id": p.id, "name": p.name, "phone": p.phone} for p in patients]
    return JsonResponse(results, safe=False)
