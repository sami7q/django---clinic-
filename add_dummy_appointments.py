from appointments.models import Appointment
from patients.models import Patient
from datetime import datetime, timedelta, time
import random

# 🗓️ إعداد البداية: من الغد
start_date = datetime.now().date() + timedelta(days=1)

# ⏰ نطاق المواعيد من 9:00 إلى 18:00، كل 30 دقيقة
start_hour = 9
end_hour = 18
slot_duration = 30  # دقيقة

# 🧍 المرضى الحاليين
patients = list(Patient.objects.all())

if not patients:
    print("⚠️ لا يوجد مرضى في قاعدة البيانات، أضف مرضى أولاً.")
else:
    Appointment.objects.all().delete()  # ← اختياري لمسح المواعيد القديمة
    print(f"🧹 تم تنظيف المواعيد القديمة ({len(patients)} مريض متاح).")

    total_slots_per_day = ((end_hour - start_hour) * 60) // slot_duration
    total_patients = len(patients)
    total_days = (total_patients // total_slots_per_day) + 1

    appointment_id = 0
    for day_offset in range(total_days):
        current_date = start_date + timedelta(days=day_offset)
        for slot_index in range(total_slots_per_day):
            if appointment_id >= total_patients:
                break
            patient = patients[appointment_id]
            appointment_id += 1

            slot_time = (datetime.combine(current_date, time(start_hour, 0)) +
                         timedelta(minutes=slot_index * slot_duration)).time()

            Appointment.objects.create(
                patient=patient,
                date=current_date,
                time=slot_time,
                reason=random.choice([
                    "مراجعة طبية", "فحص دوري", "متابعة علاج", "ألم مفاجئ", "استشارة"
                ]),
                status="قيد الانتظار"
            )

    print(f"✅ تم إنشاء {appointment_id} موعد من تاريخ {start_date} حتى {current_date}.")
