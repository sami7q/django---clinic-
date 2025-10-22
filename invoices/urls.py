from django.urls import path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

app_name = "invoices"

@login_required
def invoices_list(request):
    return render(request, "invoices/list.html")

urlpatterns = [ path("", invoices_list, name="list") ]
