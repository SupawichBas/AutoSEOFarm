import json
import os
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from blogger_api import get_blogger_service, get_target_blog, publish_to_blogger

DATA_FILE = os.path.join("docs", "data", "articles.json")

def sync_pending_to_blogger():
    print("=" * 60)
    print("🚀 เริ่มต้นระบบซิงค์บทความขึ้น Blogger (Sync to Blogger)")
    print("=" * 60)

    if not os.path.exists(DATA_FILE):
        print(f"[!] ไม่พบไฟล์ {DATA_FILE}")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        all_articles = json.load(f)

    print(f"[*] จำนวนบทความทั้งหมดในระบบ: {len(all_articles)} บทความ")

    service = get_blogger_service()
    blog = get_target_blog(service)
    print(f"[*] บล็อกเป้าหมาย: {blog['name']} ({blog['url']})")

    # ดึงรายชื่อบทความที่มีอยู่แล้วบน Blogger ทั้งหมด (LIVE, SCHEDULED, DRAFT)
    print("[*] กำลังตรวจสอบบทความที่มีอยู่แล้วบน Blogger...")
    existing_titles = set()
    page_token = None
    while True:
        res = service.posts().list(
            blogId=blog['id'],
            status=['LIVE', 'SCHEDULED', 'DRAFT'],
            maxResults=100,
            pageToken=page_token
        ).execute()
        for p in res.get('items', []):
            existing_titles.add(p['title'].strip())
        page_token = res.get('nextPageToken')
        if not page_token:
            break

    print(f"[*] พบบทความบน Blogger แล้วทั้งหมด: {len(existing_titles)} บทความ")

    # คัดเฉพาะบทความที่ยังไม่ได้ส่งขึ้น Blogger
    pending = [a for a in all_articles if a['article_title'].strip() not in existing_titles]
    print(f"[*] พบบทความที่รอส่งขึ้น Blogger: {len(pending)} บทความ")

    if not pending:
        print("[✓] ข้อมูลบทความบน Blogger อัปเดตครบสมบูรณ์ทุกรายการแล้ว!")
        return

    success_count = 0
    quota_exhausted = False

    for idx, art in enumerate(pending, 1):
        if quota_exhausted:
            break

        print(f"\n[{idx}/{len(pending)}] กำลังโพสต์: {art['article_title'][:45]}...")
        print(f"    📅 เวลาปล่อย: {art.get('created_at', '')}")

        res_url = None
        for attempt in range(2):
            try:
                res_url = publish_to_blogger(art, blog_id=blog['id'], service=service)
                if res_url:
                    success_count += 1
                    break
            except Exception as e:
                err_str = str(e)
                if "rateLimitExceeded" in err_str or "quota" in err_str.lower() or "429" in err_str:
                    print(f"    [!] ถึงขีดจำกัดโควตา API รายวันของ Google Blogger")
                    quota_exhausted = True
                    break
                print(f"    [!] เกิดข้อผิดพลาด: {e} (กำลังลองใหม่รอบที่ {attempt+1})...")
                time.sleep(5)

        if quota_exhausted:
            print("\n[i] เนื่องจากติดโควตารายวันของ Google API สามารถนำเข้าเนื้อหาที่เหลือผ่านไฟล์ blogger_posts/blogger_import.xml ได้ทันทีในคลิกเดียว")
            break

        time.sleep(3.5)

    print("\n" + "=" * 60)
    print(f"🎉 สรุปผลการซิงค์: ส่งขึ้น Blogger สำเร็จ {success_count}/{len(pending)} รายการ")
    print(f"[*] พบบทความทั้งหมดบน Blogger ในตอนนี้: {len(existing_titles) + success_count} บทความ")
    print("=" * 60)

if __name__ == "__main__":
    sync_pending_to_blogger()
