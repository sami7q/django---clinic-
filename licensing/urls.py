from django.urls import path
from . import views

app_name = "licensing"

urlpatterns = [
    path("status/", views.status, name="status"),
    path("activate/", views.activate, name="activate"),
]
