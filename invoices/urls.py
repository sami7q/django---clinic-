from django.urls import path
from . import views

app_name = "invoices"

urlpatterns = [
    path("", views.invoice_list, name="list"),
    path("create/", views.invoice_create, name="create"),
    path("<int:id>/update/", views.invoice_update, name="update"),
    path("<int:id>/delete/", views.invoice_delete, name="delete"),
    path("summary/", views.financial_summary, name="summary"),
]
