from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Patient
from .forms import PatientForm

# 🧾 قائمة المرضى
def patients_list(request):
    patients = Patient.objects.all().order_by('-id')
    # نحولها إلى قائمة قابلة للتحويل لـ JSON
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

    return render(request, 'patients/list.html', {
        'patients_json': patients_data
    })


# 🔍 البحث عن مريض (يُستخدم في البحث الذكي داخل إضافة الموعد)
def patient_search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        patients = Patient.objects.filter(name__icontains=query)[:10]
        results = [
            {"id": p.id, "name": p.name, "phone": p.phone or ""}
            for p in patients
        ]
    return JsonResponse(results, safe=False)


# ➕ إنشاء مريض جديد من صفحة "المرضى"
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


# 🧩 إنشاء مريض عبر API (من داخل صفحة إضافة الموعد)
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


# ❌ حذف مريض (يدعم HTMX والمودال)
def delete_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        if request.headers.get('HX-Request'):
            return HttpResponse("<script>window.location.reload()</script>")
        return redirect('patients:list')
    return render(request, 'patients/delete_confirm.html', {'patient': patient})


# 👤 عرض تفاصيل المريض
def patient_detail(request, id):
    patient = get_object_or_404(Patient, id=id)
    return render(request, "patients/detail.html", {"patient": patient})


# 🧾 عرض بطاقة المريض (واجهة مبسطة أو موجزة)
def patient_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'patients/view.html', {'patient': patient})
