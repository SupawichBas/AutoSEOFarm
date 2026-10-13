import json
import os
import subprocess
import sys
import time

from feed_manager import get_next_products
from article_generator import generate_seo_article
from site_builder import update_website, load_site_articles
from blogger_exporter import export_to_blogger_format
from scheduler_helper import get_next_schedule_slots, get_latest_article_datetime, format_thai_date

# บังคับ UTF-8 สำหรับ Windows Terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

CONFIG_FILE = "config.json"
SEO_ARTICLES_DIR = "seo_articles"

def load_config():
    """โหลดการตั้งค่าระบบ"""
    default_config = {
        "ollama_url": "http://localhost:11434/api/generate",
        "model_name": "qwen2.5",
        "batch_size": 3,
        "min_sold": 5,
        "target_categories": [
            "Computers & Accessories",
            "Automobiles",
            "Mobile & Gadgets",
            "Home Appliances",
            "Audio"
        ],
        "site_title": "Shopee Tech & Auto Review",
        "site_description": "ศูนย์รวมรีวิวสินค้าไอที จัดโต๊ะคอม อุปกรณ์แต่งรถ และแกดเจ็ตยอดนิยม คุ้มค่าน่าซื้อ",
        "site_url": "https://username.github.io/ShopeeAutoSEOFarm",
        "auto_git_push": True
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                default_config.update(loaded)
        except Exception as e:
            print(f"[!] Warning reading config: {e}")
    return default_config

def save_markdown_file(article):
    """บันทึกไฟล์ Markdown ดิบลงในโฟลเดอร์ seo_articles"""
    os.makedirs(SEO_ARTICLES_DIR, exist_ok=True)
    filename = f"{article['slug']}.md"
    filepath = os.path.join(SEO_ARTICLES_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(article["content_markdown"])
    return filepath

def git_commit_and_push(article_count):
    """สั่ง Git Add, Commit และ Push ขึ้น GitHub อัตโนมัติ (สำหรับ GitHub Pages)"""
    try:
        # ตรวจสอบว่ามี Git repository หรือยัง
        subprocess.run(["git", "status"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        # ถ้ายังไม่มี ให้ git init
        print("[*] กำลังสร้าง Git repository เบื้องต้น...")
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "branch", "-M", "main"], check=True)

    try:
        print("[*] กำลังซิงค์ไฟล์ขึ้น Git...")
        # เพิ่มไฟล์ทั้งหมด ยกเว้น CSV ขนาดใหญ่ (เราจะสร้าง .gitignore ให้กันไว้)
        subprocess.run(["git", "add", "docs/", "seo_articles/", "blogger_posts/", "config.json", "history.json"], check=False)
        commit_msg = f"Auto SEO Update: Add {article_count} new articles ({time.strftime('%Y-%m-%d %H:%M')})"
        subprocess.run(["git", "commit", "-m", commit_msg], check=False)
        
        # ตรวจสอบว่ามี Remote Origin หรือไม่
        result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("[*] กำลัง Push ขึ้น GitHub Pages...")
            push_res = subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True)
            if push_res.returncode == 0:
                print("[✓] Push ขึ้น GitHub สำเร็จ! หน้าเว็บจะอัปเดตออนไลน์ใน 30 วินาที")
            else:
                print(f"[!] ข้อความจาก Git Push: {push_res.stderr.strip() or push_res.stdout.strip()}")
        else:
            print("[i] ยังไม่ได้ตั้งค่า Remote GitHub (ดูคำแนะนำด้านล่างเพื่อเชื่อม GitHub Repo)")
    except Exception as e:
        print(f"[!] Git warning: {e}")

def main():
    print("=" * 60)
    print("🚀 เริ่มต้นระบบ Shopee AutoSEO Farm (Full Autopilot)")
    print("=" * 60)

    config = load_config()

    # 1. คัดเลือกสินค้าใหม่จาก CSV Feed
    products = get_next_products(
        batch_size=config.get("batch_size", 5),
        target_categories=config.get("target_categories"),
        min_sold=config.get("min_sold", 5),
        min_price=config.get("min_price", 290)
    )


    if not products:
        print("[!] ไม่พบสินค้าใหม่ที่ตรงตามเงื่อนไขใน Feed")
        return

    new_articles = []

    # คำนวณช่วงเวลาปล่อยบทความแบบ Drip-feed กระจายเวลาอัตโนมัติ
    existing_articles = load_site_articles()
    latest_dt = get_latest_article_datetime(existing_articles)
    schedule_slots = get_next_schedule_slots(count=len(products), start_after=latest_dt)

    # 2. ให้ Qwen2.5 สร้างบทความ SEO พร้อมฝังวันเวลาเผยแพร่
    for idx, prod in enumerate(products, 1):
        slot_time = schedule_slots[idx - 1]
        print(f"\n[{idx}/{len(products)}] กำลังเขียนบทความ: {prod['title'][:50]}... (฿{prod['price']})")
        print(f"    📅 เวลาปล่อยบทความ: {slot_time.strftime('%Y-%m-%d %H:%M')} ({format_thai_date(slot_time)})")
        start_t = time.time()
        
        art = generate_seo_article(
            product=prod,
            ollama_url=config.get("ollama_url", "http://localhost:11434/api/generate"),
            model_name=config.get("model_name", "qwen2.5"),
            publish_time=slot_time
        )
        
        if art:
            save_markdown_file(art)
            new_articles.append(art)
            elapsed = round(time.time() - start_t, 2)
            print(f"    -> เขียนเสร็จสมบูรณ์ใน {elapsed} วินาที")
        else:
            print(f"    -> ข้ามเนื่องจากเกิดข้อผิดพลาดในการเจนเนื้อหา")

        if idx < len(products):
            time.sleep(1)

    if not new_articles:
        print("[!] ไม่มีบทความใหม่ที่สร้างสำเร็จ")
        return

    # 3. อัปเดตเว็บไซต์สำหรับ GitHub Pages
    print("\n[*] กำลังอัปเดตหน้าเว็บ GitHub Pages...")
    total_site_articles = update_website(new_articles, config)

    # 4. ส่งออกสำหรับ Blogger
    print("\n[*] กำลังจัดเตรียมบทความสำหรับ Blogger...")
    export_to_blogger_format(new_articles)

    # 4.1 โพสต์ขึ้น Blogger อัตโนมัติผ่าน Google API (ถ้ามีไฟล์กุญแจ)
    if os.path.exists("token.json") or os.path.exists("client_secret.json"):
        try:
            from blogger_api import get_blogger_service, get_target_blog, publish_to_blogger
            print("\n[*] กำลังส่งบทความขึ้น Blogger อัตโนมัติ...")
            b_service = get_blogger_service()
            b_blog = get_target_blog(b_service)
            success_blogger = 0
            for art in new_articles:
                res_url = None
                for attempt in range(2):
                    res_url = publish_to_blogger(art, blog_id=b_blog['id'], service=b_service)
                    if res_url:
                        success_blogger += 1
                        break
                    print("    [!] รอ 10 วินาทีเพื่อลองส่งขึ้น Blogger ใหม่อีกครั้ง...")
                    time.sleep(10)
                time.sleep(3.5)
            print(f"[*] โพสต์ขึ้น Blogger เรียบร้อยทั้งหมด {success_blogger}/{len(new_articles)} บทความ")
        except Exception as e:
            print(f"[!] Blogger Auto-Post notice: {e}")



    # 5. ซิงค์ขึ้น GitHub
    if config.get("auto_git_push", True):
        print("\n[*] ทำการบันทึกสถานะผ่าน Git...")
        git_commit_and_push(len(new_articles))

    print("\n" + "=" * 60)
    print("🎉 สรุปผลการทำงาน:")
    print(f"- ผลิตบทความใหม่: {len(new_articles)} บทความ")
    print(f"- รวมบทความบนเว็บทั้งหมด: {total_site_articles} บทความ")
    print(f"- เว็บไซต์พร้อมเปิดดูได้ที่: docs/index.html")
    print(f"- บทความสำหรับ Blogger อยู่ที่: blogger_posts/")
    print("=" * 60)

if __name__ == "__main__":
    main()
