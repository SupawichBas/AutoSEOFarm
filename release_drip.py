import argparse
import datetime
import json
import os
import subprocess
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from site_builder import update_website, load_site_articles
from blogger_exporter import export_to_blogger_format
from scheduler_helper import format_thai_date, to_iso_local, format_price

QUEUE_FILE = "article_queue.json"
DATA_FILE = os.path.join("docs", "data", "articles.json")
CONFIG_FILE = "config.json"

def get_git_branch():
    try:
        res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return "main"

def load_json(filepath, default_val):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default_val

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def release_drip(count=1):
    print("=" * 60)
    print(f"💧 ปล่อยบทความทีละนิด (Drip Release): จำนวน {count} บทความ")
    print("=" * 60)

    queue = load_json(QUEUE_FILE, [])
    if not queue:
        print("[!] ไม่มีบทความค้างในคิว (Queue ว่างเปล่า)")
        return

    config = load_json(CONFIG_FILE, {})
    live_articles = load_json(DATA_FILE, [])

    released = []
    now = datetime.datetime.now()
    release_count = min(count, len(queue))

    for i in range(release_count):
        art = queue.pop(0)
        # หากปล่อยหลายบทความพร้อมกัน ให้กระจายเวลาย้อนหลังทีละ 2 ชั่วโมงเพื่อให้เป็นธรรมชาติ
        offset_hours = (release_count - 1 - i) * 2
        art_time = now - datetime.timedelta(hours=offset_hours)
        
        art["created_at"] = art_time.strftime("%Y-%m-%d %H:%M:%S")
        art["date_iso"] = to_iso_local(art_time)
        
        live_articles.insert(0, art) # เพิ่มไว้บนสุด
        released.append(art)
        print(f"\n[✓] ปล่อยบทความ ({i+1}/{release_count}): {art['article_title']}")
        print(f"    - สินค้า: {art['product_title'][:40]}... (฿{format_price(art['price'])})")
        print(f"    - วันเวลาเผยแพร่: {art['created_at']} ({format_thai_date(art['created_at'])})")

    # บันทึกคิวที่เหลือ และบทความที่ออนไลน์อยู่
    save_json(QUEUE_FILE, queue)
    save_json(DATA_FILE, live_articles)

    # รีบิลด์เว็บไซต์
    print("\n[*] กำลังอัปเดตหน้าเว็บและ Sitemap...")
    update_website(live_articles, config)
    export_to_blogger_format(released)
    # ซิงค์ Git
    if config.get("auto_git_push", True):
        try:
            curr_branch = get_git_branch()
            subprocess.run(["git", "add", "docs/", "article_queue.json", "blogger_posts/"], check=False)
            commit_msg = f"Drip release: Add {len(released)} article(s) ({now.strftime('%Y-%m-%d %H:%M')})"
            subprocess.run(["git", "commit", "-m", commit_msg], check=False)
            subprocess.run(["git", "push", "origin", curr_branch], check=False)
            print(f"[✓] ซิงค์ขึ้น GitHub ({curr_branch}) เรียบร้อย")
        except Exception as e:
            print(f"[!] Git notice: {e}")

    print("\n" + "=" * 60)
    print(f"🎉 สรุปการปล่อยบทความ:")
    print(f"- ปล่อยบทความใหม่: {len(released)} รายการ")
    print(f"- รวมบทความออนไลน์ในเว็บ: {len(live_articles)} รายการ")
    print(f"- คงเหลือในคิวรอปล่อย: {len(queue)} รายการ")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Drip release articles gradually")
    parser.add_argument("--count", type=int, default=1, help="จำนวนบทความที่ต้องการปล่อย (ค่าเริ่มต้น 1)")
    args = parser.parse_args()
    release_drip(args.count)
