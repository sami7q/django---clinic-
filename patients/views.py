from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from .models import Patient
from .forms import PatientForm


# 🧾 قائمة المرضى
@login_required
def patients_list(request):
    patients = Patient.objects.all().order_by('-id')
    patients_data = [
        {
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "gender": p.gender,
            "phone": p.phone or "",
            "diagnosis": p.diagnosis or "",
            "notes": p.notes or "",
            "created_at": p.created_at.isoformat(),
        }
        for p in patients
    ]
    return render(request, 'patients/list.html', {'patients_json': patients_data})


# 🔍 البحث الذكي داخل صفحة إضافة الموعد
@login_required
def patient_search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        patients = Patient.objects.filter(name__icontains=query)[:10]
        results = [{"id": p.id, "name": p.name, "phone": p.phone or ""} for p in patients]
    return JsonResponse(results, safe=False)


# ➕ إنشاء مريض جديد (من صفحة المرضى)
@login_required
def create_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_at = timezone.now()
            patient.save()
            messages.success(request, "✅ تم إضافة المريض بنجاح.")
            return redirect('patients:list')
    else:
        form = PatientForm()
    return render(request, 'patients/create.html', {'form': form})


# 🧩 إنشاء مريض عبر API (للاستخدام من صفحة إضافة الموعد)
@csrf_exempt
def patient_create_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            patient = Patient.objects.create(
                name=data.get('name', ''),
                phone=data.get('phone', ''),
                age=data.get('age', None),
                gender=data.get('gender', ''),
                diagnosis=data.get('diagnosis', ''),
                created_at=timezone.now(),
            )
            return JsonResponse({
                "id": patient.id,
                "name": patient.name,
                "phone": patient.phone
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)


# ✏️ تعديل بيانات المريض
@login_required
def edit_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ تم تعديل بيانات المريض بنجاح.")
            return redirect('patients:view', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patients/edit.html', {'form': form, 'patient': patient})


# ❌ حذف مريض
@login_required
def delete_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, "🗑️ تم حذف المريض بنجاح.")
        return redirect('patients:list')
    return render(request, 'patients/delete_confirm.html', {'patient': patient})


# 👤 عرض تفاصيل المريض
@login_required
def patient_detail(request, id):
    patient = get_object_or_404(Patient, id=id)
    return render(request, "patients/detail.html", {"patient": patient})


# 🧾 عرض السجل الطبي أو البطاقة الموسعة
@login_required
def patient_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'patients/view.html', {'patient': patient})
