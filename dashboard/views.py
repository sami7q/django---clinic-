from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def home(request):
    stats = {
        "patients_today": 0,
        "appointments_today": 0,
        "invoices_today": 0,
    }
    return render(request, "dashboard/home.html", {"stats": stats})
