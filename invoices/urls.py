from django.urls import path
from . import views

app_name = "invoices"

urlpatterns = [
    # 🧾 الفواتير
    path("", views.invoice_list, name="list"),
    path("filter/<str:period>/", views.invoice_filter, name="filter"),
    path("create/", views.invoice_create, name="create"),
    path("<int:pk>/update/", views.invoice_update, name="update"),
    path("<int:pk>/delete/", views.invoice_delete, name="delete"),
    path("<int:pk>/print/", views.invoice_print, name="print"),
    path("print/latest/", views.print_latest_invoice, name="print_latest"),

    # 💸 النفقات
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/create/", views.expense_create, name="expense_create"),

    # 🔍 بحث المريض
    path("patient-search/", views.patient_search, name="patient_search"),
]
