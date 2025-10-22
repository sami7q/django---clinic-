from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patients_list, name='list'),
    path('create/', views.create_patient, name='create'),
    path('<int:pk>/view/', views.patient_view, name='view'),
    path('<int:pk>/delete/', views.delete_patient, name='delete'),
]
