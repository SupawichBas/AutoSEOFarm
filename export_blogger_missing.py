"""
สร้างไฟล์นำเข้า Blogger แยกต่างหาก "เฉพาะบทความที่ยังไม่มีบน Blogger"
- เทียบชื่อบทความกับที่มีบน Blogger อยู่แล้ว (กันนำเข้าซ้ำ)
- แยกไฟล์ตามวันที่เผยแพร่ -> blogger_posts/import/blogger_import_YYYY-MM-DD.xml
  (นำเข้าทีละไฟล์ได้ ถ้าโดน Google จำกัดจำนวนครั้ง ค่อยทำไฟล์ถัดไปวันหลัง)

วิธีรัน:  python export_blogger_missing.py
"""
import json
import os
import sys
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from blogger_api import get_blogger_service, get_target_blog
from blogger_exporter import export_to_blogger_format, BLOGGER_DIR

DATA_FILE = os.path.join("docs", "data", "articles.json")
OUT_DIR = os.path.join(BLOGGER_DIR, "import")


def fetch_existing_titles():
    service = get_blogger_service()
    blog = get_target_blog(service)
    titles, token = set(), None
    while True:
        res = service.posts().list(
            blogId=blog["id"],
            status=["LIVE", "SCHEDULED", "DRAFT"],
            maxResults=100,
            pageToken=token,
        ).execute()
        for p in res.get("items", []):
            titles.add(p["title"].strip())
        token = res.get("nextPageToken")
        if not token:
            return titles


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        articles = json.load(f)

    existing = fetch_existing_titles()
    missing = [a for a in articles if a["article_title"].strip() not in existing]
    print(f"[*] บทความบนเว็บ {len(articles)} | อยู่บน Blogger แล้ว {len(articles) - len(missing)} | ยังไม่มี {len(missing)}")

    if not missing:
        print("[✓] Blogger มีครบแล้ว ไม่ต้องนำเข้าอะไรเพิ่ม")
        return

    # ล้างไฟล์แยกเก่า แล้วสร้างใหม่ให้ตรงกับสถานะปัจจุบัน
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in os.listdir(OUT_DIR):
        if name.startswith("blogger_import_") and name.endswith(".xml"):
            os.remove(os.path.join(OUT_DIR, name))

    by_day = defaultdict(list)
    for a in missing:
        by_day[(a.get("created_at") or "unknown")[:10]].append(a)

    files = []
    for day in sorted(by_day):
        path = os.path.join(OUT_DIR, f"blogger_import_{day}.xml")
        export_to_blogger_format(by_day[day], xml_path=path)
        files.append((path, len(by_day[day])))

    print("\n[✓] ไฟล์ที่ต้องนำเข้า (ทำทีละไฟล์):")
    for path, n in files:
        print(f"    - {path}  ({n} บทความ)")


if __name__ == "__main__":
    main()
