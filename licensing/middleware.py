from django.shortcuts import redirect
from .models import LicenseKey

class LicenseCheckMiddleware:
    """يتأكد من وجود رخصة فعّالة قبل الدخول للنظام"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exempt_paths = ["/licenses/activate/", "/licenses/status/", "/admin/"]

        # السماح بالوصول إلى الصفحات المستثناة
        if any(request.path.startswith(path) for path in exempt_paths):
            return self.get_response(request)

        # فحص الرخصة
        key = LicenseKey.objects.first()
        if not key or not key.is_active or key.is_expired:
            return redirect("licensing:activate")

        return self.get_response(request)
