"""
========================================================================================
🏢 SHOPEE AUTO-SEO FARM: VIRTUAL EXECUTIVE HEADQUARTERS (CEO PIPELINE)
========================================================================================
ระบบบริหารงานองค์กรเสมือนจริง (Virtual Organization Pipeline)
บทบาทในทีม:
  👑 Chief Executive Officer (CEO): ควบคุมกลยุทธ์, กำกับ KPI และสั่งการทั้งระบบ
  🕵️ Product Scout (นักวิเคราะห์ตลาด): คัดสรรสินค้าคุณภาพสูง ยอดขายดี จาก CSV Feed
  ✍️ Senior Copywriter (นักเขียนคอนเทนต์ SEO): ร่างบทความมุมมองสดใหม่ และฟอร์แมตราคา
  🛡️ QA Inspector / Tester (ผู้ตรวจสอบคุณภาพ): Gatekeeper สแกนภาษาจีน, คำต้องห้าม, จุลภาคราคา >= 1,000
  🚀 Release Manager (ผู้จัดการฝ่ายเผยแพร่): นำบทความเข้าคิว Staging และ Drip-feed ขึ้น Production
========================================================================================
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import time

from feed_manager import get_next_products
from article_generator import generate_seo_article
from qa_inspector import inspect_article, run_qa_suite
from site_builder import update_website, load_site_articles
from blogger_exporter import export_to_blogger_format
from scheduler_helper import (
    get_next_schedule_slots,
    get_latest_article_datetime,
    format_thai_date,
    format_price,
    get_git_branch
)
from release_drip import release_drip

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

CONFIG_FILE = "config.json"
QUEUE_FILE = "article_queue.json"
DATA_FILE = os.path.join("docs", "data", "articles.json")

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

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║        🏢 SHOPEE AUTO-SEO FARM: VIRTUAL COMPANY PIPELINE         ║
║          Executive Dashboard & Multi-Role Autopilot Suite        ║
╚══════════════════════════════════════════════════════════════════╝
""")

def show_dashboard():
    config = load_json(CONFIG_FILE, {})
    queue = load_json(QUEUE_FILE, [])
    live = load_json(DATA_FILE, [])
    
    # คำนวณราคาสูงสุดและราคาเฉลี่ย
    prices = []
    for art in live:
        try:
            prices.append(float(str(art.get("price", "0")).replace(",", "")))
        except ValueError:
            pass
    avg_price = sum(prices) / len(prices) if prices else 0
    max_price = max(prices) if prices else 0

    curr_branch = get_git_branch()
    branch_labels = {
        "main": "🟢 main (Production / หน้าเว็บจริง)",
        "release": "🟡 release (Staging / ตรวจสอบก่อนปล่อยจริง)",
        "develop": "🔵 develop (Development / พัฒนาและร่างบทความ)"
    }
    branch_display = branch_labels.get(curr_branch, f"⚪ {curr_branch}")

    print("=" * 66)
    print("📊 รายงานสรุปผลงานระดับผู้บริหาร (Executive KPI Dashboard)")
    print("=" * 66)
    print(f"  🌿 สภาพแวดล้อม (Git Branch)         : {branch_display}")
    print(f"  🌐 เว็บไซต์หลัก (Primary Platform) : {config.get('site_url', 'N/A')}")
    print(f"  🚀 บทความออนไลน์ (Live Production) : {len(live)} บทความ")
    print(f"  📦 บทความในคิวรอปล่อย (Staging Queue) : {len(queue)} บทความ")
    print(f"  💰 สถิติราคาสินค้าในระบบ             : เฉลี่ย ฿{avg_price:,.0f} (สูงสุด ฿{max_price:,.0f})")
    print(f"  🛡️ นโยบายการโพสต์ Blogger API       : {'เปิดใช้งาน' if config.get('enable_blogger_api') else 'เซฟตี้โหมด (นำเข้าผ่าน XML ปลอดภัย 100%)'}")
    print(f"  ⚙️ AI Model เครื่องหลัก             : {config.get('model_name', 'qwen2.5')}")
    print("=" * 66)

def run_sprint_pipeline(count=5, direct_to_queue=True):
    """
    รันกระบวนการทำงานทั้งบริษัท (Complete Sprint Pipeline):
    1. CEO กำหนดเป้าหมาย
    2. Scout คัดเลือกสินค้า
    3. Copywriter ผลิตบทความ
    4. QA Tester ทดสอบและ Auto-Heal ก่อนขึ้น Staging
    5. Release Manager จัดคิวหรือปล่อยบทความ
    """
    print("\n" + "=" * 66)
    print(f"👑 [CEO]: มอบหมายงานสปรินต์ ผลิตบทความ SEO คุณภาพสูงจำนวน {count} บทความ")
    print("=" * 66)

    config = load_json(CONFIG_FILE, {})
    
    # Step 1: Product Scout
    print("\n🕵️ [Product Scout]: กำลังสำรวจ CSV Feed เพื่อหาสินค้า High-Conversion...")
    products = get_next_products(
        batch_size=count,
        target_categories=config.get("target_categories"),
        min_sold=config.get("min_sold", 5),
        min_price=config.get("min_price", 290)
    )

    if not products:
        print("  [!] Scout รายงาน: ไม่พบสินค้าใหม่ที่ตรงตามเกณฑ์ใน Feed")
        return

    print(f"  [✓] Scout คัดสรรสินค้าสำเร็จ {len(products)} รายการ:")
    for p in products:
        print(f"      - {p['title'][:45]}... (฿{format_price(p['price'])}) | ขายแล้ว {p['sold']}")

    # คำนวณช่วงเวลาปล่อยบทความ
    queue = load_json(QUEUE_FILE, [])
    live = load_json(DATA_FILE, [])
    base_articles = queue if queue else live
    latest_dt = get_latest_article_datetime(base_articles)
    schedule_slots = get_next_schedule_slots(count=len(products), start_after=latest_dt)

    approved_articles = []
    rejected_count = 0

    # Step 2 & 3: Copywriter + QA Inspector Gate
    print("\n✍️ [Copywriter & QA Gate]: เริ่มต้นเขียนบทความและทดสอบคุณภาพแบบเข้มงวด...")
    for idx, prod in enumerate(products, 1):
        slot_time = schedule_slots[idx - 1]
        print(f"\n[{idx}/{len(products)}] สินค้า: {prod['title'][:40]}... (฿{format_price(prod['price'])})")
        print(f"    📅 วางแผนเผยแพร่: {slot_time.strftime('%Y-%m-%d %H:%M')} ({format_thai_date(slot_time)})")
        
        # ร่างบทความ
        t_start = time.time()
        art = generate_seo_article(
            product=prod,
            ollama_url=config.get("ollama_url", "http://localhost:11434/api/generate"),
            model_name=config.get("model_name", "qwen2.5"),
            publish_time=slot_time
        )

        if not art:
            print("    [!] Copywriter เกิดข้อผิดพลาดในการเจนเนอเรท ข้ามบทความนี้")
            rejected_count += 1
            continue

        # ส่งเข้าห้องทดสอบ QA Inspector Gate
        qa_result = inspect_article(art, auto_heal=True)
        elapsed = round(time.time() - t_start, 2)

        if qa_result["passed"]:
            clean_art = qa_result["article"]
            approved_articles.append(clean_art)
            heal_summary = f" [Auto-Healed {len(qa_result['heal_log'])} รายการ]" if qa_result["healed"] else ""
            print(f"    🛡️ [QA PASSED: {qa_result['score']}/100]{heal_summary} อนุมัติผ่านเกณฑ์ใน {elapsed}s")
            if qa_result["healed"]:
                for h in qa_result["heal_log"]:
                    print(f"       - ซ่อมแซม: {h}")
        else:
            print(f"    ❌ [QA REJECTED: {qa_result['score']}/100] ไม่ผ่านเกณฑ์มาตรฐานความปลอดภัย ปฏิเสธการเผยแพร่")
            rejected_count += 1

        if idx < len(products):
            time.sleep(1)

    if not approved_articles:
        print("\n[!] ไม่มีบทความที่ผ่านการทดสอบ QA")
        return

    # Step 4: Release Manager (Staging vs Direct Production)
    print("\n🚀 [Release Manager]: นำบทความที่ผ่าน QA เข้าสู่ระบบ...")
    if direct_to_queue:
        queue.extend(approved_articles)
        save_json(QUEUE_FILE, queue)
        print(f"  [✓] นำเข้า Staging Queue สำเร็จ {len(approved_articles)} บทความ (คิวรวมปัจจุบัน: {len(queue)} บทความ)")
        print(f"  [i] แนะนำ: ใช้คำสั่ง Drip Release เพื่อทยอยปล่อยขึ้นเว็บจริงและ Blogger อย่างเป็นธรรมชาติ")
    else:
        # ปล่อยขึ้น Production ทันที
        update_website(approved_articles, config)
        export_to_blogger_format(approved_articles)
        print(f"  [✓] เผยแพร่ขึ้น Live Production สำเร็จ {len(approved_articles)} บทความ")

    # บันทึกไฟล์ดิบ Markdown
    os.makedirs("seo_articles", exist_ok=True)
    for art in approved_articles:
        with open(os.path.join("seo_articles", f"{art['slug']}.md"), "w", encoding="utf-8") as f:
            f.write(art["content_markdown"])

    # สรุปผลลัพธ์รอบการทำงาน
    print("\n" + "=" * 66)
    print("🏆 [CEO REPORT]: สรุปผลการดำเนินงานของทีมงานทั้งหมด")
    print(f"  - คัดเลือกสินค้าใหม่ : {len(products)} รายการ")
    print(f"  - ผ่าน QA & อนุมัติ   : {len(approved_articles)} บทความ (คะแนนเฉลี่ย >= 85)")
    print(f"  - ปฏิเสธ (ไม่ผ่านเกณฑ์) : {rejected_count} บทความ")
    print(f"  - สถานะคิวปัจจุบัน     : {len(queue)} บทความรอปล่อย")
    print("=" * 66)


def git_switch_branch(target):
    try:
        res = subprocess.run(["git", "checkout", target], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[✓] สลับไปยัง Branch '{target}' สำเร็จ")
            return True
        print(f"[!] ไม่สามารถสลับ Branch ได้: {res.stderr.strip() or res.stdout.strip()}")
        return False
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

def git_promote_branch(source, target):
    try:
        print(f"[*] กำลังสลับไปที่ Branch '{target}'...")
        res_co = subprocess.run(["git", "checkout", target], capture_output=True, text=True)
        if res_co.returncode != 0:
            print(f"[!] ล้มเหลวในการ checkout '{target}': {res_co.stderr.strip()}")
            return False
        
        print(f"[*] กำลังรวมงาน (Merge) จาก '{source}' เข้าสู่ '{target}'...")
        res_mg = subprocess.run(["git", "merge", source, "-m", f"Promote {source} to {target}"], capture_output=True, text=True)
        if res_mg.returncode != 0:
            print(f"[!] ไม่สามารถ Merge ได้: {res_mg.stderr.strip() or res_mg.stdout.strip()}")
            return False
        
        print(f"[*] กำลัง Push '{target}' ขึ้น GitHub...")
        res_push = subprocess.run(["git", "push", "origin", target], capture_output=True, text=True)
        if res_push.returncode == 0:
            print(f"[✓] รวมงานจาก '{source}' -> '{target}' และซิงค์ขึ้น GitHub สำเร็จสมบูรณ์!")
            return True
        else:
            print(f"[!] ข้อความจาก Git Push: {res_push.stderr.strip() or res_push.stdout.strip()}")
            return False
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

def git_branch_menu():
    while True:
        curr = get_git_branch()
        print("\n" + "=" * 66)
        print(f"🌿 บริหารจัดการกิ่ง Git Branches (ปัจจุบันอยู่ที่: {curr})")
        print("=" * 66)
        print("  [1] สลับไปที่ 'develop' (กิ่งพัฒนา, ร่างบทความ, วิจัย Feed)")
        print("  [2] สลับไปที่ 'release' (กิ่ง Staging, ตรวจสอบ QA ก่อนปล่อย)")
        print("  [3] สลับไปที่ 'main'    (กิ่ง Production จริง, แสดงผลบน GitHub Pages)")
        print("  ----------------------------------------------------------------")
        print("  [4] 🚀 รวมงาน: develop  -->  release (ส่งบทความเข้าคิว Staging)")
        print("  [5] 🏆 ปล่อยจริง: release -->  main    (ปล่อยบทความที่ผ่าน QA ขึ้น Live Website)")
        print("  [0] กลับสู่เมนูหลัก")

        sub_choice = input("\n👉 กรุณาเลือกคำสั่ง [0-5]: ").strip()
        if sub_choice == "1":
            git_switch_branch("develop")
        elif sub_choice == "2":
            git_switch_branch("release")
        elif sub_choice == "3":
            git_switch_branch("main")
        elif sub_choice == "4":
            confirm = input("ยืนยันการรวมงานจาก develop เข้าสู่ release หรือไม่? (y/n): ").strip().lower()
            if confirm == "y":
                git_promote_branch("develop", "release")
        elif sub_choice == "5":
            confirm = input("ยืนยันการปล่อยงานจาก release ขึ้น main (Production Live) หรือไม่? (y/n): ").strip().lower()
            if confirm == "y":
                git_promote_branch("release", "main")
        elif sub_choice == "0":
            break
        else:
            print("[!] คำสั่งไม่ถูกต้อง")
        time.sleep(1)

def interactive_menu():
    while True:
        print_banner()
        show_dashboard()
        print("\nเมนูสั่งการระดับผู้บริหาร (Executive Commands):")
        print("  [1] 🚀 รันงานสปรินต์ครบวงจร (Scout -> Write -> QA Test -> เข้าคิว Staging)")
        print("  [2] 🛡️ รัน QA Inspector ตรวจสอบระบบ (ตรวจภาษาจีน, คำต้องห้าม, ฟอร์แมตราคา 1,000)")
        print("  [3] 💧 Release Manager: ปล่อยบทความจากคิวขึ้นเว็บจริง (Drip Feed)")
        print("  [4] 🌐 รีบิลด์และอัปเดตหน้าเว็บจริง (GitHub Pages Rebuild)")
        print("  [5] 📄 อัปเดตและส่งออกไฟล์ Blogger XML (สำหรับ 1-Click Import)")
        print("  [6] 📊 รีเฟรชดูรายงานสถานะระบบ (Dashboard)")
        print("  [7] 🌿 บริหารจัดการ Git Branches (develop / release / main)")
        print("  [0] ออกจากระบบ")
        
        try:
            choice = input("\n👉 กรุณาเลือกคำสั่ง [0-7]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nปิดการทำงานของระบบ CEO Pipeline")
            break

        if choice == "1":
            try:
                cnt_str = input("จำนวนบทความที่ต้องการสร้างในสปรินต์นี้ [ค่าเริ่มต้น 5]: ").strip()
                count = int(cnt_str) if cnt_str else 5
            except ValueError:
                count = 5
            run_sprint_pipeline(count=count, direct_to_queue=True)
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")
        elif choice == "2":
            run_qa_suite()
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")
        elif choice == "3":
            try:
                cnt_str = input("ต้องการปล่อยบทความกี่บทความ [ค่าเริ่มต้น 1]: ").strip()
                count = int(cnt_str) if cnt_str else 1
            except ValueError:
                count = 1
            release_drip(count)
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")
        elif choice == "4":
            config = load_json(CONFIG_FILE, {})
            live = load_json(DATA_FILE, [])
            update_website(live, config)
            print("[✓] รีบิลด์หน้าเว็บ GitHub Pages เรียบร้อย (docs/index.html และ docs/articles/)")
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")
        elif choice == "5":
            live = load_json(DATA_FILE, [])
            export_to_blogger_format(live)
            print("[✓] ส่งออก Blogger XML เรียบร้อย (อยู่ที่ blogger_posts/blogger_import.xml)")
            input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")
        elif choice == "6":
            continue
        elif choice == "7":
            git_branch_menu()
        elif choice == "0":
            print("\nปิดการทำงานของระบบ CEO Pipeline เรียบร้อย")
            break
        else:
            print("[!] คำสั่งไม่ถูกต้อง กรุณาเลือกหมายเลข 0-7")
            time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="Shopee AutoSEO Farm: CEO Orchestrator")
    parser.add_argument("--sprint", type=int, help="รัน Sprint อัตโนมัติระบุจำนวนบทความ เช่น --sprint 5")
    parser.add_argument("--drip", type=int, help="ปล่อยบทความจากคิว Staging สู่ Production เช่น --drip 3")
    parser.add_argument("--qa", action="store_true", help="รัน QA Inspector Audit ทั้งระบบ")
    parser.add_argument("--dashboard", action="store_true", help="แสดงแดชบอร์ดสรุปผลงานระดับผู้บริหาร")
    args = parser.parse_args()

    if args.sprint:
        run_sprint_pipeline(count=args.sprint, direct_to_queue=True)
    elif args.drip:
        release_drip(args.drip)
    elif args.qa:
        run_qa_suite()
    elif args.dashboard:
        show_dashboard()
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
