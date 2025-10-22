from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LicenseKey

MASTER_LICENSE_CODE = "IQ-SAMI-CLINIC-2025"

def activate(request):
    """صفحة تفعيل النظام"""
    key = LicenseKey.objects.first()

    # ✅ إذا الرخصة موجودة وصالحة → لا داعي لإعادة التفعيل
    if key and key.is_valid():
        return redirect("login")

    # 🔄 في حالة إرسال الكود
    if request.method == "POST":
        code = request.POST.get("code", "").strip()

        if code == MASTER_LICENSE_CODE:
            if not key:
                key = LicenseKey.objects.create()
            key.activate(code)
            messages.success(request, "✅ تم تفعيل النظام بنجاح لمدة 30 يومًا. يرجى تسجيل الدخول الآن.")
            return redirect("login")
        else:
            messages.error(request, "❌ كود التفعيل غير صالح.")

    return render(request, "licensing/activate.html")
