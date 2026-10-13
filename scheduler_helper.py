import datetime
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ช่วงเวลาทองของการซื้อขายออนไลน์ในไทย (Golden Hours)
# 08:30 (ช่วงเดินทาง/เริ่มงาน)
# 12:15 (ช่วงพักกลางวัน)
# 18:30 (ช่วงเดินทางกลับ/เลิกงาน)
# 21:00 (ช่วง Flash Sale 21:00 / ช้อปก่อนนอน)
PEAK_HOURS = [(8, 30), (12, 15), (18, 30), (21, 0)]

THAI_MONTHS = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]
THAI_MONTHS_SHORT = [
    "", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
    "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."
]

def parse_datetime(dt_val):
    """แปลงค่าวันเวลาหลากฟอร์แมตให้เป็น datetime object (timezone-naive)"""
    if isinstance(dt_val, datetime.datetime):
        return dt_val.replace(tzinfo=None) if dt_val.tzinfo else dt_val
    if not dt_val or not isinstance(dt_val, str):
        return datetime.datetime.now()
    
    clean_val = dt_val.replace("Z", "+00:00")
    try:
        if "T" in clean_val:
            dt = datetime.datetime.fromisoformat(clean_val)
            return dt.replace(tzinfo=None)
        return datetime.datetime.strptime(clean_val, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.datetime.now()

def format_thai_date(dt_val, short=False):
    """จัดรูปแบบวันเวลาภาษาไทยให้อ่านง่าย เช่น 13 ต.ค. 2026 เวลา 21:00 น."""
    dt = parse_datetime(dt_val)
    months = THAI_MONTHS_SHORT if short else THAI_MONTHS
    return f"{dt.day} {months[dt.month]} {dt.year} เวลา {dt.strftime('%H:%M')} น."

def to_rfc3339_utc(dt_val):
    """แปลง datetime (เวลาท้องถิ่นไทย UTC+7) เป็น ISO RFC3339 UTC สำหรับ Google Blogger"""
    dt = parse_datetime(dt_val)
    # สมมติเวลาในเครื่องเป็นเวลาไทย (UTC+7)
    utc_dt = dt - datetime.timedelta(hours=7)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def to_iso_local(dt_val):
    """แปลง datetime เป็น ISO 8601 พร้อมระบุ +07:00 สำหรับ Schema.org"""
    dt = parse_datetime(dt_val)
    return dt.strftime("%Y-%m-%dT%H:%M:%S+07:00")

def get_latest_article_datetime(articles):
    """ค้นหาเวลาเผยแพร่ล่าสุดจากบทความที่มีอยู่ เพื่อต่อคิวตารางเวลาอย่างต่อเนื่อง"""
    if not articles:
        return None
    latest_dt = None
    for art in articles:
        dt = parse_datetime(art.get("created_at") or art.get("date_iso"))
        if latest_dt is None or dt > latest_dt:
            latest_dt = dt
    return latest_dt

def get_next_schedule_slots(count, start_after=None):
    """
    คำนวณช่วงเวลาปล่อยบทความแบบ Drip-feed กระจายตามช่วงเวลาทอง (Golden Hours)
    หากไม่ระบุ start_after จะเริ่มจากเวลาปัจจุบัน
    """
    base_time = parse_datetime(start_after) if start_after else datetime.datetime.now()
    # หากเวลาที่ส่งมาเก่ากว่าปัจจุบัน ให้เริ่มจากปัจจุบัน
    now = datetime.datetime.now()
    if base_time < now:
        base_time = now

    slots = []
    current_date = base_time.date()

    while len(slots) < count:
        for hour, minute in PEAK_HOURS:
            slot_dt = datetime.datetime(current_date.year, current_date.month, current_date.day, hour, minute)
            if slot_dt > base_time:
                slots.append(slot_dt)
                if len(slots) == count:
                    break
        current_date += datetime.timedelta(days=1)

    return slots
