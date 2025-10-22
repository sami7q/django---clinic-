from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import LicenseKey
from .forms import ActivateForm

def status(request):
    return render(request, "licensing/status.html")

def activate(request):
    if request.method == "POST":
        form = ActivateForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data["key"].strip()
            try:
                lic = LicenseKey.objects.get(key=key)
                if lic.is_valid():
                    # خزّن الحالة في الجلسة لمرة أولى (بساطة مبدئية)
                    request.session["license_ok"] = True
                    request.session["license_expires"] = lic.expires_at.isoformat()
                    messages.success(request, "تم التفعيل بنجاح.")
                    return redirect("dashboard:home")
                else:
                    messages.error(request, "الكود غير صالح أو منتهي.")
            except LicenseKey.DoesNotExist:
                messages.error(request, "الكود غير موجود.")
    else:
        form = ActivateForm()
    return render(request, "licensing/activate.html", {"form": form})
