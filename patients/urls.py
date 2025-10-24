from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('search/', views.patient_search, name='search'),                     # البحث عن مريض (لخاصية البحث الذكي)
    path('create_api/', views.patient_create_api, name='create_api'),          # API لإضافة مريض من داخل صفحة الموعد
    path('', views.patients_list, name='list'),                               # قائمة المرضى
    path('create/', views.create_patient, name='create'),                      # إنشاء مريض جديد يدويًا
    path('<int:pk>/view/', views.patient_view, name='view'),                   # عرض بطاقة المريض
    path('<int:pk>/delete/', views.delete_patient, name='delete'),             # حذف مريض
    path('<int:id>/', views.patient_detail, name='detail'),                    # عرض تفاصيل المريض
]
