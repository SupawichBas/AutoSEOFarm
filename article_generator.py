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


def generate_seo_article(product, ollama_url="http://localhost:11434/api/generate", model_name="qwen2.5"):
    """ใช้ Qwen2.5 เขียนบทความ SEO คุณภาพสูงที่กระตุ้นยอดคลิก"""
    title = product["title"]
    price = product["price"]
    sold = product["sold"]
    category = product["category"]
    affiliate_link = product["affiliate_link"]
    image_url = product["image"]

    prompt = f"""
คุณคือนักเขียนบล็อกและผู้เชี่ยวชาญด้าน SEO การตลาด Affiliate ภาษาไทย
ช่วยเขียนบทความรีวิวและแนะนำสินค้าสำหรับ: '{title}'
หมวดหมู่: {category}
ราคาประมาณ: {price} บาท (มียอดขายแล้วกว่า {sold} ชิ้น)

ข้อกำหนดโครงสร้างบทความ (Markdown):
1. หัวข้อหลัก (H1): ตั้งชื่อให้น่าสนใจ มีคีย์เวิร์ด และชวนคลิกอ่าน เช่น 'รีวิว... คุ้มไหม ดีจริงหรือหลอก?'
2. รูปภาพสินค้า: ใส่ลิงก์รูปนี้ที่ด้านบนของบทความ: ![{title}]({image_url})
3. ปัญหาและความต้องการ (Pain Points): ปัญหานี้แก้ได้อย่างไร ทำไมสินค้านี้ถึงจำเป็น
4. จุดเด่นและสเปกสำคัญ (Bullet points): จุดที่น่าสนใจ ทำไมคนถึงซื้อเยอะ
5. ข้อควรพิจารณา / สรุปความคุ้มค่า: รีวิวอย่างเป็นกลาง น่าเชื่อถือ
6. กล่อง Call-To-Action (CTA) สรุปท้ายบทความ:
   - ข้อความกระตุ้นให้กดเช็คโปร เช่น '🔥 เช็คราคาโปรโมชั่นล่าสุด + เก็บโค้ดส่งฟรี Shopee ได้ที่นี่'
   - ใส่ปุ่มลิงก์ชัดเจน: [👉 ดูราคาพิเศษและสั่งซื้อผ่าน Shopee คลิกลิ้งก์นี้]({affiliate_link})

ข้อควรระวัง:
- ใช้ภาษาไทยที่เป็นธรรมชาติ น่าอ่าน เหมือนผู้เชี่ยวชาญรีวิวเอง ไม่เหมือนบอทแปล
- ไม่ต้องใส่คำอธิบายการทำงานของ prompt ตอบเฉพาะตัวบทความเท่านั้น
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
            h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            article_title = h1_match.group(1).strip() if h1_match else title

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
