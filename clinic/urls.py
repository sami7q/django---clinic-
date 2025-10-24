from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from licensing.models import LicenseKey


def home_redirect(request):
    """تحكم في الصفحة الرئيسية بناءً على حالة التفعيل"""
    key = LicenseKey.objects.first()
    if not key or not key.is_active:
        return redirect("licensing:activate")
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    return redirect("login")


urlpatterns = [
    # ✅ الصفحة الرئيسية تعتمد على حالة التفعيل
    path("", home_redirect),

    # 🧩 لوحات النظام
    path("admin/", admin.site.urls),
    path("licensing/", include(("licensing.urls", "licensing"), namespace="licensing")),
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
    path("patients/", include(("patients.urls", "patients"), namespace="patients")),
    path("appointments/", include(("appointments.urls", "appointments"), namespace="appointments")),
    path("invoices/", include(("invoices.urls", "invoices"), namespace="invoices")),

    # 👥 قسم المستخدمين — تم إصلاح التكرار هنا
    path("users/", include(("users.urls", "users"), namespace="users")),

    # 🔐 نظام تسجيل الدخول والخروج الافتراضي من Django
    path("auth/", include("django.contrib.auth.urls")),
]
