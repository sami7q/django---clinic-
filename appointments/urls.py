from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='list'),
    path('create/', views.appointment_create, name='create'),
    path('<int:id>/update/', views.appointment_update, name='update'),
    path('<int:id>/delete/', views.appointment_delete, name='delete'),
]
