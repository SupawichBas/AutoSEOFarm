import datetime
import html
import os
import sys
import markdown

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


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
        exported_files.append((art, blogger_html))

    # สร้างไฟล์ blogger_import.xml สำหรับนำเข้าแบบคลิกเดียวผ่านเมนู "นำเข้าเนื้อหา"
    generate_blogger_xml(exported_files)

    print(f"[*] บันทึกบทความสำหรับ Blogger ไว้ในโฟลเดอร์ '{BLOGGER_DIR}' เรียบร้อย ({len(exported_files)} ไฟล์)")
    return [f[0] for f in exported_files]

def generate_blogger_xml(articles_with_html):
    """สร้างไฟล์ XML มาตรฐาน Blogger Atom สำหรับนำเข้าทั้งหมดในคลิกเดียว"""
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    entries_xml = []
    for art, full_html in articles_with_html:
        # ตัด comment ด้านบนออกเพื่อเอาเฉพาะ HTML เนื้อหา
        content_only = full_html.split("-->\n\n", 1)[-1] if "-->\n\n" in full_html else full_html
        escaped_content = html.escape(content_only)
        escaped_title = html.escape(art["article_title"])
        escaped_cat = html.escape(art["category"])

        entry = f"""  <entry>
    <id>tag:blogger.com,1999:blog-0.post-{art['id']}</id>
    <published>{now_iso}</published>
    <updated>{now_iso}</updated>
    <title type='text'>{escaped_title}</title>
    <content type='html'>{escaped_content}</content>
    <category scheme='http://schemas.google.com/g/2005#kind' term='http://schemas.google.com/blogger/2008/kind#post'/>
    <category scheme='http://www.blogger.com/atom/ns#' term='{escaped_cat}'/>
    <category scheme='http://www.blogger.com/atom/ns#' term='Shopee'/>
    <category scheme='http://www.blogger.com/atom/ns#' term='รีวิวสินค้า'/>
    <status>LIVE</status>
  </entry>"""
        entries_xml.append(entry)

    feed_xml = f"""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom' 
      xmlns:openSearch='http://a9.com/-/spec/opensearchrss/1.0/' 
      xmlns:blogger='http://schemas.google.com/blogger/2008' 
      xmlns:georss='http://www.georss.org/georss' 
      xmlns:gd='http://schemas.google.com/g/2005' 
      xmlns:thr='http://purl.org/syndication/thread/1.0'>
  <id>tag:blogger.com,1999:blog-0</id>
  <updated>{now_iso}</updated>
  <title type='text'>Shopee Review</title>
{"\n".join(entries_xml)}
</feed>
"""
    xml_path = os.path.join(BLOGGER_DIR, "blogger_import.xml")
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(feed_xml)
    print(f"[*] สร้างไฟล์นำเข้าบล็อกเกอร์แบบรวม: {xml_path}")

