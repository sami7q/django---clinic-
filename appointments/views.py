from django.shortcuts import render, redirect, get_object_or_404
from .models import Appointment
from .forms import AppointmentForm


def appointment_list(request):
    appointments = Appointment.objects.all().order_by('-date', '-time')
    return render(request, 'appointments/list.html', {'appointments': appointments})


def appointment_create(request):
    form = AppointmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('appointments:list')
    return render(request, 'appointments/create.html', {'form': form})


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
