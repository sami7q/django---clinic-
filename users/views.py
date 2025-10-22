from django.shortcuts import render
from django.contrib.auth.models import User

def user_list(request):
    users = User.objects.all()
    return render(request, "users/list.html", {"users": users})
