import requests
import json
import os
import sys
import time

# บังคับรองรับการแสดงผลภาษาไทย (UTF-8) บน Windows Terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# ==========================================
# 1. Configuration (ตั้งค่าระบบ)
# ==========================================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5"
OUTPUT_DIR = "seo_articles"

# ลิสต์สินค้าและลิงก์ Affiliate (เปลี่ยนเป็นลิงก์จริงของคุณเมื่อพร้อม)
PRODUCTS = [
    {
        "name": "เคสคอมพิวเตอร์ NZXT H7 Flow สีขาว", 
        "affiliate_link": "https://shope.ee/sample_nzxt_link"
    },
    {
        "name": "ที่วางแก้วน้ำคอนโซลกลาง ตรงรุ่น Honda Jazz GE", 
        "affiliate_link": "https://shope.ee/sample_jazz_link"
    },
    {
        "name": "เมาส์เกมมิ่งไร้สาย น้ำหนักเบา สำหรับเล่น PUBG", 
        "affiliate_link": "https://shope.ee/sample_mouse_link"
    }
]

# ==========================================
# 2. Core Functions (ฟังก์ชันหลัก)
# ==========================================
def setup_environment():
    """สร้างโฟลเดอร์สำหรับเก็บไฟล์บทความหากยังไม่มี"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[*] สร้างโฟลเดอร์ '{OUTPUT_DIR}' เรียบร้อยแล้ว")

def generate_article(product_name, affiliate_link):
    """ส่งคำสั่งให้ Qwen2.5 เขียนบทความ SEO"""
    prompt = f"""
    คุณคือนักเขียนบล็อกรีวิวสินค้ามืออาชีพ ช่วยเขียนบทความ SEO ภาษาไทยสำหรับ '{product_name}' 
    ความยาวประมาณ 500-700 คำ โครงสร้างบทความประกอบด้วย:
    1. หัวข้อหลักที่ดึงดูดความสนใจ (H1)
    2. แนะนำสินค้าเบื้องต้น และปัญหาที่สินค้านี้ช่วยแก้ได้
    3. จุดเด่นและสเปคที่น่าสนใจ (ใช้ Bullet points)
    4. สรุปความคุ้มค่า
    5. บรรทัดสุดท้ายให้ใส่ Call-to-Action ชัดเจน พร้อมแปะลิงก์นี้: {affiliate_link}
    
    ข้อควรระวัง: ใช้ภาษาที่เป็นธรรมชาติ อ่านง่าย ไม่เหมือนหุ่นยนต์แปลภาษา
    """
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            print(f"[!] Error HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"[!] Connection Error: {str(e)}")
        return None

def save_to_markdown(filename, content):
    """บันทึกเนื้อหาลงไฟล์ .md"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)
    return filepath

# ==========================================
# 3. Main Batch Process (ระบบรันอัตโนมัติ)
# ==========================================
def run_batch():
    print("=== เริ่มระบบ Shopee AutoSEO Farm ===")
    setup_environment()
    
    for index, item in enumerate(PRODUCTS, 1):
        print(f"[{index}/{len(PRODUCTS)}] กำลังประมวลผล: {item['name']}...")
        
        start_time = time.time()
        article_content = generate_article(item['name'], item['affiliate_link'])
        
        if article_content:
            # แปลงชื่อสินค้าให้เป็นชื่อไฟล์ที่ปลอดภัย (ไม่มีเว้นวรรค)
            safe_filename = item['name'].replace(" ", "_").replace("/", "_") + ".md"
            saved_path = save_to_markdown(safe_filename, article_content)
            
            elapsed_time = round(time.time() - start_time, 2)
            print(f"    -> บันทึกสำเร็จที่: {saved_path} (ใช้เวลา {elapsed_time} วินาที)")
        else:
            print(f"    -> ข้ามการบันทึกเนื่องจากเกิดข้อผิดพลาด")
        
        # พักการทำงานของการ์ดจอ 2 วินาทีก่อนเริ่มชิ้นต่อไป
        if index < len(PRODUCTS):
            time.sleep(2)

    print("\n=== ทำงานเสร็จสิ้นทั้งหมด ปิดคอมพิวเตอร์ได้เลย! ===")

if __name__ == "__main__":
    run_batch()
