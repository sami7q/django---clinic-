from django.urls import path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

app_name = "patients"

@login_required
def patients_list(request):
    return render(request, "patients/list.html")

urlpatterns = [ path("", patients_list, name="list") ]
