from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.utils.dateparse import parse_datetime
from django.utils import timezone

WHITELIST = (
    "/admin/", "/auth/login", "/auth/logout", "/__reload__/",
    "/licensing/activate", "/licensing/status",
    "/static/", "/favicon.ico",
)

class LicensingCheckMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path
        if any(path.startswith(p) for p in WHITELIST):
            return None
        ok = request.session.get("license_ok", False)
        exp_str = request.session.get("license_expires")
        request.license_ok = False
        request.license_expires = None
        if exp_str:
            exp = parse_datetime(exp_str)
            if exp and timezone.now() <= exp:
                request.license_ok = ok
                request.license_expires = exp
        if not request.license_ok:
            return redirect(reverse("licensing:activate"))
        return None
