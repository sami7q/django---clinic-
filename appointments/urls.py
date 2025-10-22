from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='list'),
    path('create/', views.appointment_create, name='create'),
    path('update/<int:id>/', views.appointment_update, name='update'),
    path('delete/<int:id>/', views.appointment_delete, name='delete'),
]
