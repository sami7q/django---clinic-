from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Patient
from .forms import PatientForm


# 🧾 قائمة المرضى
def patients_list(request):
    patients = Patient.objects.all().order_by('-id')
    return render(request, 'patients/list.html', {'patients': patients})


# ➕ إنشاء مريض جديد
def create_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_at = timezone.now()
            patient.save()
            return redirect('patients:list')
    else:
        form = PatientForm()
    return render(request, 'patients/create.html', {'form': form})


# ❌ حذف مريض
def delete_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        return redirect('patients:list')
    return render(request, 'patients/delete_confirm.html', {'patient': patient})


# 🧍‍♂️ عرض تفاصيل المريض في صفحة مستقلة
def patient_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'patients/view.html', {'patient': patient})
