from django.urls import path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

app_name = "appointments"

@login_required
def appointments_list(request):
    return render(request, "appointments/list.html")

urlpatterns = [ path("", appointments_list, name="list") ]
