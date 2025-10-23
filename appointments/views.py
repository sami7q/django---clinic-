from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import FieldDoesNotExist
from django.utils import timezone
from collections import defaultdict
from django.core.serializers import serialize
import json


from .models import Appointment
from .forms import AppointmentForm
from patients.models import Patient


def appointment_list(request):
    appointments = Appointment.objects.all().order_by('-date', '-time')
    return render(request, 'appointments/list.html', {'appointments': appointments})


def appointment_create(request):
    """
    صفحة إنشاء موعد:
    - تمرير المرضى (حاليين/قدامى إن وُجد is_active، وإلا جميعهم).
    - تمرير خريطة الحجوزات: { 'YYYY-MM-DD': ['HH:MM', ...] } لإخفاء الأوقات المحجوزة.
    """
    form = AppointmentForm(request.POST or None)

    # المرضى
    patients_active = None
    patients_archived = None
    patients = None
    try:
        Patient._meta.get_field('is_active')
        patients_active = Patient.objects.filter(is_active=True).order_by('name')
        patients_archived = Patient.objects.filter(is_active=False).order_by('name')
    except FieldDoesNotExist:
        patients = Patient.objects.all().order_by('name')

    # إعداد خريطة الحجوزات لكل تاريخ
    # (نمرر كل الحجوزات؛ بإمكانك لاحقًا تقليصها لنطاق الشهر الحالي والقادم فقط)
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
        'patients': patients,  # fallback
        'booked_slots_json': booked_slots_json,  # ← مهم للواجهة
    }
    return render(request, 'appointments/create.html', context)


def appointment_update(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    form = AppointmentForm(request.POST or None, instance=appointment)
    if form.is_valid():
        form.save()
        return redirect('appointments:list')
    return render(request, 'appointments/update.html', {'form': form})


def appointment_delete(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointments:list')
    return render(request, 'appointments/delete.html', {'appointment': appointment})

def appointment_list(request):
    appointments = Appointment.objects.all().order_by('-date', '-time')

    appointments_json = json.dumps([
        {
            "id": a.id,
            "patient": str(a.patient),
            "phone": getattr(a.patient, "phone", ""),
            "date": a.date.strftime("%Y-%m-%d"),
            "date_formatted": a.date.strftime("%d %B، %Y"),
            "time": a.time.strftime("%I:%M %p"),
            "reason": a.reason,
            "status": a.status,
            "edit_url": f"/appointments/{a.id}/update/",
            "delete_url": f"/appointments/{a.id}/delete/"
        }
        for a in appointments
    ], ensure_ascii=False)

    return render(request, 'appointments/list.html', {
        'appointments': appointments,
        'appointments_json': appointments_json
    })
