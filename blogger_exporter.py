import datetime
import html
import os
import markdown

BLOGGER_DIR = "blogger_posts"

def export_to_blogger_format(articles):
    """บันทึกไฟล์บทความให้อยู่ในฟอร์แมตที่พร้อมนำเข้า Blogger"""
    os.makedirs(BLOGGER_DIR, exist_ok=True)
    exported_files = []

    for art in articles:
        body_html = markdown.markdown(art["content_markdown"], extensions=['extra'])
        
        blogger_html = f"""<!-- 
หัวข้อบทความ (Post Title): {art['article_title']}
ป้ายกำกับ (Labels / Tags): {art['category']}, Shopee, รีวิวสินค้า
ลิงก์ภาพหน้าปก: {art['image']}
-->

<div style="font-family: Arial, sans-serif; line-height: 1.8; color: #333;">
  {body_html}

  <div style="margin-top: 30px; padding: 20px; background-color: #fff3e0; border: 2px dashed #ff9800; border-radius: 10px; text-align: center;">
    <h3 style="color: #e65100; margin-bottom: 10px;">🔥 เช็คโปรโมชั่นและโค้ดส่งฟรีล่าสุด</h3>
    <p style="margin-bottom: 15px;">สินค้าแท้ 100% สั่งตรงจากร้านค้าบน Shopee</p>
    <a href="{art['affiliate_link']}" target="_blank" rel="nofollow" 
       style="display: inline-block; background-color: #ee4d2d; color: #ffffff; padding: 12px 25px; border-radius: 5px; text-decoration: none; font-weight: bold; font-size: 16px;">
      🛒 ดูราคาพิเศษและสั่งซื้อบน Shopee คลิกที่นี่
    </a>
  </div>
</div>
"""
        filename = f"{art['slug']}.html"
        filepath = os.path.join(BLOGGER_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(blogger_html)
        exported_files.append(filepath)

    print(f"[*] บันทึกบทความสำหรับ Blogger ไว้ในโฟลเดอร์ '{BLOGGER_DIR}' เรียบร้อย ({len(exported_files)} ไฟล์)")
    return exported_files
