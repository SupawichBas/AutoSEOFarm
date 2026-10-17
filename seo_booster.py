import datetime
import html
import json
import os
import urllib.parse
import urllib.request
from scheduler_helper import format_price

DOCS_DIR = "docs"
INDEXNOW_KEY = "a8f9d2e1b4c7490192837465543210ab"

def generate_rss_feed(articles, config):
    """สร้างไฟล์ RSS 2.0 (docs/feed.xml) สำหรับระบบกระจายบทความอัตโนมัติ (Syndication/IFTTT/Pinterest/Feed Readers)"""
    site_url = config.get("site_url", "https://secguide.vercel.app").rstrip("/")
    site_title = config.get("site_title", "รีวิวสินค้าขายดี ตัวช่วยเลือกซื้อสุดคุ้ม")
    site_desc = config.get("site_description", "รวมบทความรีวิวสินค้าคุณภาพ คัดสรรเฉพาะตัวท็อป ยอดขายปัง พร้อมเปรียบเทียบสเปกและโปรโมชั่นล่าสุด")
    now_rfc822 = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    items_xml = []
    for art in articles[:50]:
        art_url = f"{site_url}/articles/{urllib.parse.quote(art['slug'])}.html"
        title = html.escape(art.get("article_title", ""))
        summary = html.escape(art.get("summary", ""))
        img = html.escape(art.get("image", ""))
        price_str = format_price(art.get("price", ""))
        aff_link = html.escape(art.get("affiliate_link", ""))
        cat = html.escape(art.get("category", "ทั่วไป"))

        desc_cdata = f"""<![CDATA[
        <p><img src="{art.get('image', '')}" alt="{title}" style="max-width:100%; border-radius:8px;" /></p>
        <p>{art.get('summary', '')}</p>
        <p><strong>ราคาพิเศษ: ฿{price_str}</strong></p>
        <p>👉 <a href="{art.get('affiliate_link', '')}">เช็คราคาโปรโมชั่นและสั่งซื้อบน Shopee คลิกที่นี่</a></p>
        <p>📖 <a href="{art_url}">อ่านรีวิวฉบับเต็ม</a></p>
        ]]>"""

        items_xml.append(f"""    <item>
      <title>{title}</title>
      <link>{art_url}</link>
      <guid isPermaLink="true">{art_url}</guid>
      <category>{cat}</category>
      <description>{desc_cdata}</description>
      <enclosure url="{img}" type="image/jpeg" />
    </item>""")

    rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{html.escape(site_title)}</title>
    <link>{site_url}/</link>
    <description>{html.escape(site_desc)}</description>
    <language>th-TH</language>
    <lastBuildDate>{now_rfc822}</lastBuildDate>
    <atom:link href="{site_url}/feed.xml" rel="self" type="application/rss+xml" />
{chr(10).join(items_xml)}
  </channel>
</rss>
"""
    feed_path = os.path.join(DOCS_DIR, "feed.xml")
    with open(feed_path, "w", encoding="utf-8") as f:
        f.write(rss_content)
    return feed_path


def generate_deals_hub(articles, config):
    """สร้างหน้ารวมพิกัดดีลด่วน (docs/index.html และ docs/deals.html) คลิกเดียวเข้า Shopee ทันที พร้อมช่องค้นหา"""
    site_url = (config.get("github_pages_url") or config.get("site_url") or "https://secguide.vercel.app").rstrip("/")
    site_title = config.get("site_title", "TechAuto Guide")

    cards = []
    for i, art in enumerate(articles):
        price_str = format_price(art.get("price", ""))
        sold = art.get("sold", 0)
        title = html.escape(art.get("product_title", art.get("article_title", "")))
        art_title = html.escape(art.get("article_title", ""))
        cat = html.escape(art.get("category", "สินค้าแนะนำ"))
        img = art.get("image") or "https://placehold.co/300x300/f1f5f9/64748b?text=Shopee"
        aff_link = art.get("affiliate_link", "#")
        review_link = f"articles/{art['slug']}.html"

        cards.append(f"""
      <div class="deal-card" data-search="{title.lower()} {art_title.lower()} {cat.lower()}">
        <div class="deal-badge">#{i+1} ขายดี</div>
        <a href="{aff_link}" target="_blank" rel="nofollow" class="deal-img-link">
          <img src="{img}" alt="{title}" loading="lazy">
        </a>
        <div class="deal-info">
          <span class="deal-cat">{cat}</span>
          <h3 class="deal-title">{title}</h3>
          <div class="deal-price-row">
            <span class="deal-price">฿{price_str}</span>
            <span class="deal-sold">ขายแล้ว {sold}+ ชิ้น</span>
          </div>
          <div class="deal-actions">
            <a href="{aff_link}" target="_blank" rel="nofollow" class="btn-buy">🛒 กดดูโปรใน Shopee</a>
            <a href="{review_link}" class="btn-review">อ่านรีวิว</a>
          </div>
        </div>
      </div>""")

    deals_html = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="google-site-verification" content="S5zS5fK-VTOFjP-FkBGa62nQHDRPGVTs-4W4k8UvkzE" />
  <title>🔥 รวมพิกัดดีลเด็ด & สินค้าขายดี Shopee | {html.escape(site_title)}</title>
  <meta name="description" content="รวมลิงก์พิกัดสินค้าขายดีคัดพิเศษ พร้อมโค้ดส่วนลดและโปรโมชั่น Shopee ล่าสุด กดสั่งซื้อได้ทันที">
  <link rel="canonical" href="{site_url}/">
  <link rel="alternate" type="application/rss+xml" title="{html.escape(site_title)} RSS" href="{site_url}/feed.xml">
  <style>
    :root {{
      --primary: #ee4d2d;
      --primary-dark: #d73211;
      --bg: #f8fafc;
      --card: #ffffff;
      --text: #0f172a;
      --muted: #64748b;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    .top-banner {{
      background: linear-gradient(135deg, #ee4d2d 0%, #ff7337 100%);
      color: white;
      text-align: center;
      padding: 2rem 1rem 2.5rem;
    }}
    .top-banner h1 {{ font-size: 1.75rem; margin-bottom: 0.4rem; }}
    .top-banner p {{ opacity: 0.92; font-size: 0.95rem; margin-bottom: 1.2rem; }}
    .search-box {{
      max-width: 520px;
      margin: -1.4rem auto 1.5rem;
      padding: 0 1rem;
    }}
    .search-box input {{
      width: 100%;
      padding: 0.9rem 1.2rem;
      border-radius: 999px;
      border: 2px solid #ffccc7;
      font-size: 1rem;
      box-shadow: 0 8px 20px rgba(0,0,0,0.08);
      outline: none;
    }}
    .search-box input:focus {{ border-color: var(--primary); }}
    .nav-bar {{
      max-width: 1100px;
      margin: 0 auto 1rem;
      padding: 0 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.9rem;
    }}
    .nav-bar a {{ color: var(--primary); text-decoration: none; font-weight: 600; }}
    .container {{
      max-width: 1100px;
      margin: 0 auto 3rem;
      padding: 0 1rem;
    }}
    .deals-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
      gap: 1rem;
    }}
    .deal-card {{
      background: var(--card);
      border-radius: 12px;
      border: 1px solid #e2e8f0;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      position: relative;
      transition: transform 0.18s, box-shadow 0.18s;
    }}
    .deal-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 10px 20px rgba(0,0,0,0.08);
    }}
    .deal-badge {{
      position: absolute;
      top: 8px;
      left: 8px;
      background: #ee4d2d;
      color: white;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 999px;
      z-index: 2;
    }}
    .deal-img-link {{
      width: 100%;
      height: 190px;
      background: #f1f5f9;
      display: block;
      overflow: hidden;
    }}
    .deal-img-link img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}
    .deal-info {{
      padding: 0.9rem;
      display: flex;
      flex-direction: column;
      flex: 1;
    }}
    .deal-cat {{
      font-size: 0.72rem;
      color: var(--primary);
      font-weight: 600;
      margin-bottom: 0.25rem;
    }}
    .deal-title {{
      font-size: 0.92rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      height: 2.75em;
    }}
    .deal-price-row {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-top: auto;
      margin-bottom: 0.75rem;
    }}
    .deal-price {{
      font-size: 1.2rem;
      font-weight: 800;
      color: var(--primary);
    }}
    .deal-sold {{
      font-size: 0.75rem;
      color: var(--muted);
    }}
    .deal-actions {{
      display: flex;
      gap: 0.4rem;
    }}
    .btn-buy {{
      flex: 1;
      background: var(--primary);
      color: white;
      text-align: center;
      padding: 0.55rem 0.5rem;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 700;
      font-size: 0.85rem;
    }}
    .btn-buy:hover {{ background: var(--primary-dark); }}
    .btn-review {{
      background: #f1f5f9;
      color: #334155;
      padding: 0.55rem 0.65rem;
      border-radius: 8px;
      text-decoration: none;
      font-size: 0.8rem;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <div class="top-banner">
    <h1>🔥 คลังพิกัดสินค้าขายดี & โปรโมชั่น Shopee</h1>
    <p>คัดเฉพาะของแท้ รีวิวแน่น กดเช็คราคาและเก็บโค้ดส่วนลดได้ทันที</p>
  </div>

  <div class="search-box">
    <input type="text" id="dealSearch" placeholder="🔍 ค้นหาชื่อสินค้า เช่น ตู้เย็น, พัดลม, ไมค์, ไส้กรอง..." oninput="filterDeals()">
  </div>

  <div class="nav-bar">
    <div style="font-weight: 600; color: #475569;">
      🛍️ คลังสินค้าแนะนำพิเศษ • ค้นหาและช้อปได้ทันที
    </div>
    <div style="display: flex; gap: 0.8rem; align-items: center;">
      <span style="font-size: 0.85rem; color: var(--muted);">สินค้า {len(articles)} รายการ</span>
    </div>
  </div>

  <div class="container">
    <div class="deals-grid" id="dealsGrid">
      {"".join(cards)}
    </div>
  </div>

  <footer style="text-align: center; padding: 2rem 1rem; color: var(--muted); font-size: 0.88rem; border-top: 1px solid #e2e8f0; margin-top: 2rem;">
    <p>© {datetime.date.today().year} {html.escape(site_title)} • <a href="feed.xml" style="color: var(--primary); text-decoration: none;">RSS Feed</a> • อัปเดตข้อมูลและราคาล่าสุดอัตโนมัติ</p>
  </footer>

  <script>
    function filterDeals() {{
      const q = document.getElementById('dealSearch').value.toLowerCase().trim();
      const cards = document.querySelectorAll('.deal-card');
      cards.forEach(c => {{
        const text = c.getAttribute('data-search') || '';
        c.style.display = text.includes(q) ? 'flex' : 'none';
      }});
    }}
  </script>
</body>
</html>
"""
    # เขียนทั้ง index.html (เป็นหน้าแรกหลัก) และ deals.html (สำหรับ backward compatibility)
    index_path = os.path.join(DOCS_DIR, "index.html")
    deals_path = os.path.join(DOCS_DIR, "deals.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(deals_html)
    with open(deals_path, "w", encoding="utf-8") as f:
        f.write(deals_html)

    # สร้างไฟล์ Key สำหรับ IndexNow
    key_path = os.path.join(DOCS_DIR, f"{INDEXNOW_KEY}.txt")
    with open(key_path, "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY)

    return index_path


def ping_search_engines(articles, config):
    """ส่งสัญญาณ Ping แจ้ง Search Engines & IndexNow อัตโนมัติโดยไม่ต้องทำมือ"""
    site_url = config.get("site_url", "https://secguide.vercel.app").rstrip("/")
    parsed = urllib.parse.urlparse(site_url)
    host = parsed.netloc

    url_list = [
        f"{site_url}/",
        f"{site_url}/deals.html",
        f"{site_url}/feed.xml",
    ]
    for art in articles[:15]:
        url_list.append(f"{site_url}/articles/{urllib.parse.quote(art['slug'])}.html")

    # 1. IndexNow API (Bing, Yahoo, Yandex, DuckDuckGo, Seznam, Naver)
    payload = {
        "host": host,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{site_url}/{INDEXNOW_KEY}.txt",
        "urlList": url_list
    }
    try:
        req = urllib.request.Request(
            "https://api.indexnow.org/indexnow",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            print(f"[✓] IndexNow Auto-Ping สำเร็จ (HTTP {resp.status}): ส่ง {len(url_list)} ลิ้งก์เข้า Search Engines ทันที")
    except Exception as e:
        print(f"[*] IndexNow Ping notice: {e}")

    # 2. Ping WebSub / PubSubHubbub Hub (แจ้งเตือน Google FeedBurner / RSS Hubs ทันทีที่อัปเดต RSS)
    try:
        hub_data = urllib.parse.urlencode({
            "hub.mode": "publish",
            "hub.url": f"{site_url}/feed.xml"
        }).encode("utf-8")
        hub_req = urllib.request.Request(
            "https://pubsubhubbub.appspot.com/",
            data=hub_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST"
        )
        with urllib.request.urlopen(hub_req, timeout=8) as resp:
            print(f"[✓] Google WebSub Hub Ping สำเร็จ (HTTP {resp.status}): กระจาย RSS Feed อัตโนมัติ")
    except Exception as e:
        print(f"[*] WebSub Ping notice: {e}")
