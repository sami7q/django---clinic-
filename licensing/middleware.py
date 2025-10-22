from django.shortcuts import redirect
from django.urls import reverse
from licensing.models import LicenseKey

class LicenseCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        excluded_paths = [
            reverse('licensing:activate'),
            reverse('admin:index'),
            '/static/', '/media/', '/auth/login/', '/auth/logout/'
        ]
        if any(request.path.startswith(path) for path in excluded_paths):
            return self.get_response(request)

        key = LicenseKey.objects.first()

        if not key or not key.is_valid():
            return redirect('licensing:activate')

        return self.get_response(request)
