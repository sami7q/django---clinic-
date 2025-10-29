import uuid
import hashlib
import platform
import subprocess

def get_raw_machine_id():
    """
    محاولة قراءه معرّف الجهاز. عدة طرق حسب النظام.
    هذه دالة مقترحة — عدلها حسب متطلباتك/المنصات المستهدفة.
    """
    try:
        # أول محاولة: mac address
        mac = uuid.getnode()
        if (mac >> 40) % 2 == 0:  # تحقق أن الماك حقيقي (unicast bit)
            return str(mac)
    except Exception:
        pass

    try:
        # على Linux حاول قراءة /etc/machine-id أو D-Bus machine id
        if platform.system() == "Linux":
            with open("/etc/machine-id", "r") as f:
                return f.read().strip()
    except Exception:
        pass

    try:
        # Windows fallback (wmic)
        if platform.system() == "Windows":
            out = subprocess.check_output(["wmic", "csproduct", "get", "uuid"], text=True)
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            if len(lines) >= 2:
                return lines[1]
    except Exception:
        pass

    # آخر ملاذ: توليد UUID محلي وحفظه في ملف داخل التطبيق (stateful)
    # ولكن هذا يمكن أن يسمح بإلغاء التثبيت وإعادة التثبيت لتجاوز القيد.
    # هنا نوفّر UUID عشوائي كـ fallback
    return str(uuid.uuid4())

def get_machine_hash():
    raw_id = get_raw_machine_id()
    return hashlib.sha256(raw_id.encode()).hexdigest()
