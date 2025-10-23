from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path("<int:id>/", views.patient_detail, name="detail"),
    path('', views.patients_list, name='list'),                     # عرض قائمة المرضى
    path('create/', views.create_patient, name='create'),            # إضافة مريض جديد
    path('<int:pk>/view/', views.patient_view, name='view'),         # عرض بطاقة المريض
    path('<int:pk>/delete/', views.delete_patient, name='delete'),   # صفحة تأكيد الحذف + تنفيذ
]
