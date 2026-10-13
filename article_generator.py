import datetime
import re
import requests
import time

def clean_slug(title, item_id):
    """แปลงชื่อสินค้าให้เป็น Slug ที่ปลอดภัยสำหรับ URL โดยเก็บสระและวรรณยุกต์ไทยครบถ้วน"""
    slug = re.sub(r'[^\u0e00-\u0e7fa-zA-Z0-9\s-]', '', title)
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')
    if not slug:
        slug = f"item-{item_id}"
    return f"{slug[:40]}-{item_id}"


import random

ANGLES = [
    {
        "style": "รีวิวเจาะลึกการใช้งานจริง",
        "headline_idea": "[รีวิวเจาะลึก] {short_title} ใช้งานจริงเป็นอย่างไร? สรุปฟังก์ชันเด็ดและข้อควรรู้",
        "tone": "เล่าถึงประสบการณ์ใช้งาน จุดประทับใจ และฟีเจอร์เด่นที่ตอบโจทย์ชีวิตประจำวัน"
    },
    {
        "style": "วิเคราะห์ความคุ้มค่าเทียบงบประมาณ",
        "headline_idea": "เปิดสเปก {short_title} ในงบ ฿{price} คุ้มค่าแค่ไหน? เจาะลึกจุดเด่นก่อนตัดสินใจซื้อ",
        "tone": "เน้นวิเคราะห์ความคุ้มค่าเทียบกับราคา จุดเด่นที่เหนือกว่า และความคุ้มราคา"
    },
    {
        "style": "คู่มือผู้ซื้อ (Buyer's Guide)",
        "headline_idea": "[สรุปครบจบ] {short_title} เหมาะกับใครบ้าง? สรุปข้อดี-ข้อสังเกตแบบตรงไปตรงมา",
        "tone": "ให้คำแนะนำชัดเจนว่าใครควรซื้อ ใครอาจต้องพิจารณา พร้อมชี้จุดเด่นและข้อจำกัดอย่างเป็นกลาง"
    },
    {
        "style": "รีวิวตอบโจทย์แก้ปัญหา",
        "headline_idea": "แก้ปัญหาตรงจุดด้วย {short_title} ไอเทมยอดนิยมที่สายนี้ต้องมีติดไว้",
        "tone": "ดึงปัญหาเดิมของผู้ใช้ขึ้นมา แล้วอธิบายว่าสินค้านี้ช่วยประหยัดเวลาหรือเพิ่มความสะดวกสบายอย่างไร"
    },
    {
        "style": "พาชมสเปกและฟีเจอร์ไฮไลต์",
        "headline_idea": "รีวิว {short_title} ไอเทมขายดี สรุปจุดเด่น สเปกหลัก และพิกัดราคาพิเศษ",
        "tone": "เน้นชูสเปกหลัก วัสดุ ดีไซน์ และการใช้งานที่สะดวกง่ายดาย"
    }
]

def generate_seo_article(product, ollama_url="http://localhost:11434/api/generate", model_name="qwen2.5"):
    """ใช้ Qwen2.5 เขียนบทความ SEO คุณภาพสูงด้วยมุมมองและสำนวนที่หลากหลาย ไม่ซ้ำซาก"""
    title = product["title"]
    price = product["price"]
    sold = product["sold"]
    category = product["category"]
    affiliate_link = product["affiliate_link"]
    image_url = product["image"]

    # ตัดชื่อสินค้าสั้นกระชับสำหรับไอเดียหัวข้อ
    short_title = title.split("|")[0].split("(")[0].strip()[:35]

    angle = random.choice(ANGLES)
    sample_h1 = angle["headline_idea"].format(short_title=short_title, price=price)

    prompt = f"""
คุณคือนักเขียนบล็อกรีวิวสินค้ามืออาชีพ สไตล์บทความมีความเป็นกันเอง สละสลวย อ่านเพลิน และน่าเชื่อถือ
แนวทางการเขียนสำหรับบทความนี้: {angle['style']} ({angle['tone']})

ข้อมูลสินค้าสำหรับรีวิว:
- ชื่อสินค้า: {title}
- หมวดหมู่: {category}
- ราคาประมาณ: {price} บาท (ยอดขายบน Shopee กว่า {sold} ชิ้น)

ข้อกำหนดโครงสร้างบทความ (Markdown):
1. หัวข้อหลัก (H1): ตั้งหัวข้อให้น่าสนใจ สื่อถึงประโยชน์ชัดเจน (ตัวอย่างแนวคิด: '{sample_h1}')
   *** ข้อห้ามเด็ดขาด: ห้ามใช้คำว่า "ดีจริงหรือหลอก?" หรือ "หลอกลวง" ในหัวข้อหรือเนื้อหาโดยเด็ดขาด! ***
2. เกริ่นนำ (Introduction): เปิดเรื่องให้น่าติดตาม เล่าถึงความน่าสนใจและทำไมสินค้านี้ถึงเป็นที่พูดถึง
3. เจาะลึกจุดเด่นและสเปกสำคัญ (Key Highlights): อธิบายฟังก์ชันหลักเป็นข้อๆ แบบเข้าใจง่าย ไม่ศัพท์เทคนิคจ๋าเกินไป
4. สรุปข้อดี vs ข้อควรสังเกต:
   - จุดเด่นที่ประทับใจ
   - ข้อสังเกตเล็กๆ น้อยๆ เพื่อความจริงใจและน่าเชื่อถือ
5. บทสรุปและความคุ้มค่า: สรุปอย่างชัดเจนว่าสินค้านี้เหมาะกับใคร คุ้มค่ากับราคา {price} บาทอย่างไร
6. ข้อเสนอพิเศษและโปรโมชั่น:
   - แนะนำการเก็บโค้ดส่วนลดและโปรโมชั่นส่งฟรี
   - ปุ่มสั่งซื้อ: [👉 ดูราคาโปรโมชั่นล่าสุดและสั่งซื้อคลิกที่นี่]({affiliate_link})

ข้อควรระวัง:
- ใช้ภาษาไทยระดับบล็อกเกอร์มืออาชีพ สำนวนลื่นไหล ไม่ทื่อ ไม่แปลกแยก
- ตอบเฉพาะตัวเนื้อหา Markdown เท่านั้น ไม่ต้องใส่คำอธิบายการรัน prompt
"""



    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    try:
        res = requests.post(ollama_url, json=payload, timeout=120)
        if res.status_code == 200:
            content = res.json().get("response", "").strip()
            
            # สกัด H1 หรือหัวข้อแรกสำหรับเป็น Post Title
            h1_match = re.search(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
            if h1_match:
                article_title = h1_match.group(1).strip()
                article_title = re.sub(r'^(หัวข้อหลัก|หัวข้อ|Title|H1)\s*[:：]\s*', '', article_title, flags=re.IGNORECASE)
                article_title = article_title.replace('**', '').replace('__', '').strip()
            else:
                article_title = sample_h1


            # สร้างสรุปสั้นๆ สำหรับ Meta Description
            clean_lines = [line.strip() for line in content.split("\n") if line.strip() and not line.startswith(('#', '!', '['))]
            summary = " ".join(clean_lines)[:160] + "..." if clean_lines else f"รีวิว {title} ราคาโปรโมชั่นล่าสุดที่ Shopee"

            slug = clean_slug(title, product["id"])

            return {
                "id": product["id"],
                "product_title": title,
                "article_title": article_title,
                "slug": slug,
                "price": price,
                "sold": sold,
                "category": category,
                "image": image_url,
                "affiliate_link": affiliate_link,
                "content_markdown": content,
                "summary": summary,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "date_iso": datetime.datetime.now().isoformat()
            }
        else:
            print(f"[!] Ollama HTTP Error: {res.status_code}")
            return None
    except Exception as e:
        print(f"[!] Error generating article: {e}")
        return None
