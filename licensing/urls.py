from django.urls import path
from . import views

app_name = "licensing"

urlpatterns = [
    path("activate/", views.activate_license, name="activate"),
    path("status/", views.license_status, name="status"),
]
