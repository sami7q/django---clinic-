from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("__reload__/", include("django_browser_reload.urls")),
    path("auth/", include("django.contrib.auth.urls")),  # login/logout/password_change...

    path("", RedirectView.as_view(pattern_name="dashboard:home", permanent=False)),
    path("dashboard/", include("dashboard.urls")),
    path("patients/", include("patients.urls")),
    path("appointments/", include("appointments.urls")),
    path("invoices/", include("invoices.urls")),
    path("licensing/", include("licensing.urls")),
]
