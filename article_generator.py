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
คุณคือนักเขียนบล็อกเกอร์รีวิวสินค้ามืออาชีพ ภาษาไทยสละสลวย เป็นกันเอง อ่านง่าย น่าเชื่อถือ
แนวทางการเขียนบทความนี้: {angle['style']} ({angle['tone']})

ข้อมูลสินค้า:
- ชื่อสินค้า: {title}
- หมวดหมู่: {category}
- ราคาประมาณ: {price} บาท (ยอดขายกว่า {sold} ชิ้น)

ข้อกำหนดสำคัญมาก:
1. บรรทัดแรกสุดของบทความ (บรรทัดที่ 1) ต้องเป็นหัวข้อหลัก โดยขึ้นต้นด้วย # เสมอ ตัวอย่างแนวคิด: '{sample_h1}'
2. *** ข้อห้ามเด็ดขาด ***:
   - เขียนเนื้อหาเป็นภาษาไทยล้วน 100% เท่านั้น ห้ามมีตัวอักษรจีน (Hanzi) หรือภาษาอื่นปนเด็ดขาด
   - ห้ามใช้คำว่า "ดีจริงหรือหลอก?" หรือ "หลอกลวง" หรือ "คุ้มไหม ดีจริงหรือหลอก?" เด็ดขาด
   - ห้ามปฏิเสธหรือขอข้อมูลเพิ่ม ให้เขียนรีวิวตามชื่อสินค้าและสเปกทันที
3. โครงสร้างเนื้อหา (Markdown):
   # [หัวข้อบทความที่น่าสนใจ ดึงดูด ชัดเจน]
   
   ## เกริ่นนำ
   (เล่าความน่าสนใจ ปัญหาที่คนมักเจอ หรือเหตุผลที่สินค้านี้ได้รับความนิยม)
   
   ## เจาะลึกจุดเด่นและสเปกสำคัญ
   (อธิบายฟังก์ชัน จุดเด่น 3-4 ข้อให้อ่านเข้าใจง่าย)
   
   ## สรุปข้อดี vs ข้อควรสังเกต
   - จุดเด่นที่ประทับใจ
   - ข้อสังเกตเล็กๆ น้อยๆ เพื่อความจริงใจ
   
   ## บทสรุปและความคุ้มค่า
   (วิเคราะห์ว่าเหมาะกับใคร ในงบประมาณ {price} บาท)
   
   ## สรุปโปรโมชั่นและพิกัดซื้อ
   👉 [ดูราคาโปรโมชั่นล่าสุดและสั่งซื้อคลิกที่นี่]({affiliate_link})

ตอบเป็นเนื้อหา Markdown ภาษาไทยล้วนเท่านั้น
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
            
            # ลบตัวอักษรจีนที่อาจเล็ดลอดออกมา (Safety Filter)
            content = re.sub(r'[\u4e00-\u9fff]+[^\n\r]*', '', content)
            
            # สกัด H1 หรือหัวข้อแรกสำหรับเป็น Post Title
            generic_sections = [
                "เจาะลึกจุดเด่น", "สเปกสำคัญ", "key highlights", "เกริ่นนำ", "introduction",
                "สรุปข้อดี", "ข้อควรสังเกต", "บทสรุป", "ข้อเสนอพิเศษ", "โปรโมชั่น", "สรุปโปรโมชั่น"
            ]
            
            h1_match = re.search(r'^#{1,3}\s+(.+)$', content, re.MULTILINE)
            extracted_title = ""
            if h1_match:
                candidate = h1_match.group(1).strip()
                candidate = re.sub(r'^(หัวข้อหลัก|หัวข้อ|Title|H1)\s*[:：]\s*', '', candidate, flags=re.IGNORECASE)
                candidate = candidate.replace('**', '').replace('__', '').strip()
                # ตรวจว่าไม่ใช่หัวข้อ section ทั่วไป
                if len(candidate) >= 8 and not any(sec in candidate.lower() for sec in generic_sections):
                    extracted_title = candidate

            article_title = extracted_title if extracted_title else sample_h1

            # ตรวจสอบว่าบรรทัดแรกเริ่มด้วย H1 หรือไม่ ถ้าไม่ ให้ใส่ให้ถูกต้อง
            if not content.startswith("#"):
                content = f"# {article_title}\n\n{content}"

            # สร้างสรุปสั้นๆ สำหรับ Meta Description
            clean_lines = [line.strip() for line in content.split("\n") if line.strip() and not line.startswith(('#', '!', '['))]
            summary = " ".join(clean_lines)[:160] + "..." if clean_lines else f"รีวิว {title} สรุปสเปกและราคาโปรโมชั่นล่าสุด"

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
