import json, hashlib, uuid, platform, subprocess
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from django.db import transaction
from .models import LicenseKey, UsedLicense
from django.db.utils import IntegrityError


# 🔒 مفتاح سري مشترك بين المولد والنظام (يجب أن يتطابق تمامًا)
SECRET = "IQCLINIC2025-SECURE-HASH"


# 🧠 دالة للحصول على معرف الجهاز (Machine ID)
def get_machine_hash():
    """
    إرجاع هاش فريد يمثل الجهاز الحالي.
    يعتمد على MAC address أو machine-id حسب النظام.
    """
    try:
        # أولاً نحاول قراءة /etc/machine-id في لينكس
        if platform.system() == "Linux":
            with open("/etc/machine-id", "r") as f:
                raw_id = f.read().strip()
        # في ويندوز نقرأ UUID الجهاز
        elif platform.system() == "Windows":
            out = subprocess.check_output(["wmic", "csproduct", "get", "uuid"], text=True)
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            raw_id = lines[1] if len(lines) > 1 else str(uuid.getnode())
        else:
            raw_id = str(uuid.getnode())
    except Exception:
        raw_id = str(uuid.getnode())

    # نحول المعرف إلى SHA256 لتخزينه بأمان
    return hashlib.sha256(raw_id.encode()).hexdigest()


# 🧩 دالة التحقق من التوقيع القادم من المولد
def verify_signature(data, signature):
    """
    تتحقق من صحة التوقيع المرسل داخل ملف الترخيص
    عبر إعادة حساب SHA256 بنفس القاعدة التي يستخدمها المولد.
    """
    try:
        raw = f"{data['device_id']}{data['issued_at']}{data['expires_at']}{data['nonce']}{data.get('allowed_devices', 1)}{SECRET}"
        digest = hashlib.sha256(raw.encode()).hexdigest()
        return digest == signature
    except Exception:
        return False


# 🔑 صفحة رفع وتفعيل الترخيص
def activate_license(request):
    """
    تستقبل ملف JSON من المولد، تتحقق من التوقيع والتواريخ،
    وتربط التفعيل بعدد الأجهزة المحدد.
    """
    if request.method == "POST" and request.FILES.get("license_file"):
        try:
            file = request.FILES["license_file"]
            data = json.load(file)

            # ✅ تحقق من وجود الحقول الأساسية
            required_fields = ["device_id", "issued_at", "expires_at", "nonce", "signature", "allowed_devices"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing field: {field}")

            # ✅ تحقق من التوقيع القادم من المولد
            if not verify_signature(data, data["signature"]):
                messages.error(request, "❌ كود التفعيل غير صالح أو تم تعديله.")
                return redirect("licensing:activate")

            # ✅ تحقق من الوقت وصلاحية الترخيص
            now = timezone.now()
            issued = timezone.make_aware(datetime.fromisoformat(data["issued_at"]))
            expires = timezone.make_aware(datetime.fromisoformat(data["expires_at"]))

            if now < issued or now > expires:
                messages.error(request, "⏰ انتهت صلاحية الكود أو الوقت غير مطابق.")
                return redirect("licensing:activate")

            # ✅ احصل على معرف الجهاز الحالي
            machine_hash = get_machine_hash()

            # ✅ نستخدم معاملة آمنة لمنع السباق
            with transaction.atomic():
                # هل هناك ترخيص بنفس التوقيع؟
                license_obj = LicenseKey.objects.filter(signature=data["signature"]).first()

                if not license_obj:
                    # أول تفعيل للكود — ننشئه في قاعدة البيانات
                    license_obj = LicenseKey.objects.create(
                        device_id=data["device_id"],
                        expires_at=expires,
                        is_active=True,
                        signature=data["signature"],
                        allowed_devices=int(data.get("allowed_devices", 1)),
                        remaining_devices=int(data.get("allowed_devices", 1))
                    )

                # تحقق من انتهاء الترخيص
                if license_obj.expires_at < timezone.now():
                    messages.error(request, "⏰ انتهت صلاحية الترخيص.")
                    return redirect("licensing:activate")

                # هل الجهاز مفعل مسبقًا؟
                if hasattr(license_obj, "registered_devices") and \
                   license_obj.registered_devices.filter(machine_hash=machine_hash).exists():
                    messages.info(request, "✅ هذا الجهاز مفعل مسبقًا.")
                    return redirect("licensing:status")

                # تحقق من توفر حصة تفعيل
                if license_obj.remaining_devices <= 0:
                    messages.error(request, "⚠️ تم استهلاك الحد الأقصى للأجهزة المسموح بها.")
                    return redirect("licensing:activate")

                # ✅ سجل الجهاز الجديد وأنقص العدد
                from .models import RegisteredDevice
                RegisteredDevice.objects.create(license=license_obj, machine_hash=machine_hash)
                license_obj.remaining_devices -= 1
                license_obj.save()

                # سجل الاستخدام
                UsedLicense.objects.get_or_create(signature=data["signature"])

            messages.success(request, "✅ تم تفعيل النظام بنجاح على هذا الجهاز.")
            return redirect("licensing:status")

        except json.JSONDecodeError:
            messages.error(request, "⚠️ الملف ليس بصيغة JSON صالحة.")
        except IntegrityError:
            messages.warning(request, "⚠️ هذا الجهاز مفعل مسبقًا.")
        except Exception as e:
            messages.error(request, f"❌ خطأ أثناء التفعيل: {e}")

        return redirect("licensing:activate")

    return render(request, "licensing/activate.html")


# 🧾 صفحة حالة الترخيص الحالية
def license_status(request):
    """
    تعرض حالة الترخيص الحالية وعدد الأجهزة المتبقية.
    """
    key = LicenseKey.objects.first()
    status = "❌ لا يوجد ترخيص مفعل"
    devices_info = []

    if key:
        now = timezone.now()
        if key.expires_at > now:
            remaining_days = (key.expires_at - now).days
            status = f"✅ مرخّص حتى {key.expires_at.date()} ({remaining_days} يوم متبقٍ)"
        else:
            status = f"⏰ انتهت صلاحية الترخيص بتاريخ {key.expires_at.date()}"

        from .models import RegisteredDevice
        devices_info = list(key.registered_devices.all())

    return render(
        request,
        "licensing/status.html",
        {"key": key, "license_status": status, "devices_info": devices_info},
    )
