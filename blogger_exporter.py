import datetime
import html
import os
import re
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
        # ลบรูปซ้ำในเนื้อหา markdown (ถ้ามี) เพื่อให้รูปบนสุดเป็นมาตรฐานเดียว
        clean_md = re.sub(r'!\[.*?\]\(.*?\)', '', art["content_markdown"])
        body_html = markdown.markdown(clean_md, extensions=['extra'])
        img_url = art.get("image") or ""
        
        blogger_html = f"""<!-- 
หัวข้อบทความ (Post Title): {art['article_title']}
ป้ายกำกับ (Labels / Tags): {art['category']}, Shopee, รีวิวสินค้า
ลิงก์ภาพหน้าปก: {img_url}
-->

<div style="font-family: Arial, sans-serif; line-height: 1.8; color: #333;">
  <div class="separator" style="clear: both; text-align: center; margin-bottom: 25px;">
    <a href="{img_url}" style="margin-left: 1em; margin-right: 1em;">
      <img border="0" data-original-height="800" data-original-width="800" src="{img_url}" alt="{html.escape(art['article_title'])}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />
    </a>
  </div>

  {body_html}

  <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; margin: 25px 0; padding: 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; color: #475569;">
    <span>🛡️ รับประกันของแท้ 100%</span>
    <span>🚚 จัดส่งฟรีทั่วไทย</span>
    <span>💳 มีเก็บเงินปลายทาง</span>
    <span>⚡ สินค้าคุณภาพ ขายดี</span>
  </div>

  <div style="margin-top: 30px; padding: 25px 15px; background-color: #fff7ed; border: 2px dashed #f97316; border-radius: 12px; text-align: center;">
    <h3 style="color: #c2410c; margin-bottom: 8px; font-size: 20px;">🔥 เช็คราคาโปรโมชั่นและโค้ดลด Shopee ล่าสุด</h3>
    <p style="margin-bottom: 15px; color: #7c2d12;">ราคาพิเศษเพียง ฿{art['price']} • มียอดขายแล้วกว่า {art['sold']} ชิ้น</p>
    <div style="display: flex; flex-direction: column; gap: 12px; max-width: 420px; margin: 0 auto;">
      <a href="{art['affiliate_link']}" target="_blank" rel="nofollow" 
         style="display: block; background-color: #ee4d2d; color: #ffffff !important; padding: 14px 25px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">
        🛒 ดูราคาโปรโมชั่นล่าสุดใน Shopee (คลิก)
      </a>
      <a href="{art['affiliate_link']}" target="_blank" rel="nofollow" 
         style="display: block; background-color: #f59e0b; color: #78350f !important; padding: 12px 25px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 15px;">
        🎟️ เก็บโค้ดลด Shopee & โค้ดส่งฟรีวันนี้
      </a>
    </div>
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
        img_url = art.get("image", "")

        entry = f"""  <entry>
    <id>tag:blogger.com,1999:blog-0.post-{art['id']}</id>
    <published>{now_iso}</published>
    <updated>{now_iso}</updated>
    <title type='text'>{escaped_title}</title>
    <content type='html'>{escaped_content}</content>
    <media:thumbnail xmlns:media='http://search.yahoo.com/mrss/' url='{img_url}' height='400' width='400'/>
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

