from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("", views.appointments_list, name="list"),
    path("all/", views.appointments_all, name="all"),
    path("create/", views.appointment_create, name="create"),
    path("<int:pk>/edit/", views.appointment_update, name="edit"),
    path("<int:pk>/delete/", views.appointment_delete, name="delete"),
]
