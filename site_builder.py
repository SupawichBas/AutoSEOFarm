import datetime
import html
import json
import os
import sys
import markdown

from scheduler_helper import format_thai_date, parse_datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


DOCS_DIR = "docs"
ARTICLES_DIR = os.path.join(DOCS_DIR, "articles")
DATA_FILE = os.path.join(DOCS_DIR, "data", "articles.json")

BASE_CSS = """
:root {
  --primary: #ee4d2d;
  --primary-hover: #d73211;
  --bg: #f8fafc;
  --card-bg: #ffffff;
  --text: #1e293b;
  --text-muted: #64748b;
  --border: #e2e8f0;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--bg);
  color: var(--text);
  line-height: 1.6;
}
header {
  background: white;
  border-bottom: 1px solid var(--border);
  padding: 1rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.header-container {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.logo {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary);
  text-decoration: none;
}
.container {
  max-width: 1100px;
  margin: 2rem auto;
  padding: 0 1rem;
}
.hero {
  text-align: center;
  margin-bottom: 2.5rem;
}
.hero h1 { font-size: 2.2rem; color: #0f172a; margin-bottom: 0.5rem; }
.hero p { color: var(--text-muted); font-size: 1.1rem; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}
.card {
  background: var(--card-bg);
  border-radius: 12px;
  border: 1px solid var(--border);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.08);
}
.card-img-wrap {
  width: 100%;
  height: 220px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card-body {
  padding: 1.25rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.badge {
  display: inline-block;
  background: #fff1f0;
  color: var(--primary);
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 0.5rem;
}
.card-title a {
  color: var(--text);
  text-decoration: none;
}
.card-title a:hover { color: var(--primary); }
.card-price {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary);
  margin-top: auto;
  padding-top: 0.5rem;
}
.btn {
  display: inline-block;
  background: var(--primary);
  color: white !important;
  font-weight: 600;
  text-decoration: none;
  padding: 0.65rem 1.25rem;
  border-radius: 8px;
  text-align: center;
  transition: background 0.2s;
  margin-top: 0.75rem;
}
.btn:hover { background: var(--primary-hover); }
/* Article Page */
.article-wrap {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 2.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.02);
}
.article-meta {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 1rem;
}
.article-content img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 1.5rem 0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.article-content h1, .article-content h2, .article-content h3 {
  color: #0f172a;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}
.article-content p { margin-bottom: 1rem; }
.article-content ul, .article-content ol { margin-left: 1.5rem; margin-bottom: 1rem; }
.trust-badges {
  display: flex;
  justify-content: center;
  gap: 1.25rem;
  flex-wrap: wrap;
  margin: 1.5rem 0;
  padding: 0.85rem;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.85rem;
  color: #475569;
}
.trust-badge-item {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 500;
}
.cta-box {
  background: #fff7ed;
  border: 2px dashed #f97316;
  border-radius: 12px;
  padding: 1.75rem 1.25rem;
  margin-top: 2rem;
  text-align: center;
}
.cta-box h3 { color: #c2410c; margin-bottom: 0.5rem; font-size: 1.3rem; }
.cta-buttons-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 480px;
  margin: 1.25rem auto 0 auto;
}
.btn-voucher {
  display: inline-block;
  background: #f59e0b;
  color: #78350f !important;
  font-weight: 700;
  text-decoration: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-align: center;
  transition: opacity 0.2s;
}
.btn-voucher:hover { opacity: 0.9; }
/* Mobile Sticky Bottom CTA */
.sticky-mobile-cta {
  display: none;
}
footer {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
  font-size: 0.85rem;
  border-top: 1px solid var(--border);
  margin-top: 4rem;
  background: white;
}
@media (max-width: 768px) {
  body { padding-bottom: 75px; }
  .article-wrap { padding: 1.25rem; }
  .hero h1 { font-size: 1.6rem; }
  .sticky-mobile-cta {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    padding: 0.65rem 1rem;
    box-shadow: 0 -4px 15px rgba(0,0,0,0.12);
    align-items: center;
    justify-content: space-between;
    z-index: 999;
    border-top: 1px solid var(--border);
  }
  .sticky-info {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding-right: 0.5rem;
  }
  .sticky-title {
    font-size: 0.8rem;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: var(--text);
  }
  .sticky-price {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--primary);
  }
  .btn-sticky {
    background: var(--primary);
    color: white !important;
    font-weight: 700;
    font-size: 0.85rem;
    padding: 0.6rem 1.25rem;
    border-radius: 8px;
    text-decoration: none;
    white-space: nowrap;
    flex-shrink: 0;
  }
}

"""

def init_dirs():
    """สร้างโฟลเดอร์สำหรับ Static Site"""
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, "data"), exist_ok=True)

def load_site_articles():
    """โหลดข้อมูลบทความทั้งหมดที่เคยสร้างไว้"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Warning reading articles data: {e}")
            return []
    return []

def save_site_articles(articles):
    """บันทึกข้อมูลบทความทั้งหมด"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

def build_article_page(art, config):
    """สร้างไฟล์ HTML สำหรับหน้ารายละเอียดบทความ"""
    site_url = config.get("site_url", "https://mysite.github.io").rstrip("/")
    site_title = config.get("site_title", "Shopee Reviews")
    article_url = f"{site_url}/articles/{art['slug']}.html"

    # แปลง Markdown เป็น HTML
    body_html = markdown.markdown(art["content_markdown"], extensions=['extra'])

    thai_pub_date = format_thai_date(art.get('created_at') or art.get('date_iso'))
    pub_iso = art.get("date_iso") or art.get("created_at")

    # JSON-LD Schema สำหรับ Google Search
    schema_json = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": art["product_title"],
        "image": art["image"],
        "description": art["summary"],
        "datePublished": pub_iso,
        "dateModified": pub_iso,
        "offers": {
            "@type": "Offer",
            "price": art["price"],
            "priceCurrency": "THB",
            "availability": "https://schema.org/InStock",
            "url": art["affiliate_link"]
        }
    }

    html_template = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(art['article_title'])} | {html.escape(site_title)}</title>
  <meta name="description" content="{html.escape(art['summary'])}">
  <link rel="canonical" href="{article_url}">
  
  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="{html.escape(art['article_title'])}">
  <meta property="og:description" content="{html.escape(art['summary'])}">
  <meta property="og:image" content="{art['image']}">
  <meta property="og:url" content="{article_url}">
  
  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(art['article_title'])}">
  <meta name="twitter:description" content="{html.escape(art['summary'])}">
  <meta name="twitter:image" content="{art['image']}">
  
  <script type="application/ld+json">
  {json.dumps(schema_json, ensure_ascii=False, indent=2)}
  </script>
  
  <style>{BASE_CSS}</style>
</head>
<body>
  <header>
    <div class="header-container">
      <a href="../index.html" class="logo">← {html.escape(site_title)}</a>
      <span class="badge">{html.escape(art['category'])}</span>
    </div>
  </header>

  <main class="container">
    <article class="article-wrap">
      <div class="article-meta">
        <span>📅 เผยแพร่เมื่อ: {thai_pub_date}</span> • 
        <span>หมวดหมู่: {html.escape(art['category'])}</span> • 
        <span>ขายแล้วกว่า: {art['sold']} ชิ้น</span>
      </div>

      <div class="article-content">
        {body_html}
      </div>

      <div class="trust-badges">
        <div class="trust-badge-item">🛡️ ของแท้ 100%</div>
        <div class="trust-badge-item">🚚 จัดส่งรวดเร็วทั่วไทย</div>
        <div class="trust-badge-item">💳 มีเก็บเงินปลายทาง</div>
        <div class="trust-badge-item">⚡ คุ้มค่า ราคาพิเศษ</div>
      </div>

      <div class="cta-box">
        <h3>🔥 เช็คราคาโปรโมชั่นและโค้ดลด Shopee ล่าสุด</h3>
        <p style="margin-bottom: 0.5rem; color: #7c2d12;">ราคาพิเศษเพียง ฿{art['price']} • มียอดขายแล้วกว่า {art['sold']} ชิ้น</p>
        <div class="cta-buttons-wrap">
          <a href="{art['affiliate_link']}" target="_blank" rel="nofollow noopener" class="btn" style="font-size: 1.05rem; padding: 0.85rem 1.5rem;">
            🛒 ดูราคาโปรโมชั่นล่าสุดใน Shopee (คลิก)
          </a>
          <a href="{art['affiliate_link']}" target="_blank" rel="nofollow noopener" class="btn-voucher">
            🎟️ เก็บโค้ดลด Shopee & โค้ดส่งฟรีวันนี้
          </a>
        </div>
      </div>
    </article>
  </main>

  <div class="sticky-mobile-cta">
    <div class="sticky-info">
      <span class="sticky-title">{html.escape(art['product_title'])}</span>
      <span class="sticky-price">฿{art['price']}</span>
    </div>
    <a href="{art['affiliate_link']}" target="_blank" rel="nofollow noopener" class="btn-sticky">
      🛒 สั่งซื้อเลย
    </a>
  </div>

  <footer>
    <p>© {datetime.date.today().year} {html.escape(site_title)} • เว็บไซต์รีวิวสินค้าแนะนำพร้อมลิงก์โปรโมชั่น</p>
  </footer>
</body>
</html>

"""
    file_path = os.path.join(ARTICLES_DIR, f"{art['slug']}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    return file_path

def build_index_page(articles, config):
    """สร้างหน้าแรก (Homepage) แสดงการ์ดรีวิวสินค้าทั้งหมด"""
    site_title = config.get("site_title", "Shopee Reviews")
    site_desc = config.get("site_description", "ศูนย์รวมรีวิวสินค้าคุณภาพ")
    site_url = config.get("site_url", "https://mysite.github.io").rstrip("/")

    cards_html = []
    # เรียงจากบทความใหม่ล่าสุดไปเก่าสุด
    sorted_articles = sorted(articles, key=lambda x: x.get("created_at", ""), reverse=True)

    for art in sorted_articles:
        img_src = art.get("image") or "https://via.placeholder.com/400x300?text=Shopee+Review"
        thai_date_card = format_thai_date(art.get('created_at') or art.get('date_iso'), short=True)
        card = f"""
      <div class="card">
        <div class="card-img-wrap">
          <img src="{img_src}" alt="{html.escape(art['product_title'])}" class="card-img" loading="lazy">
        </div>
        <div class="card-body">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
            <span class="badge">{html.escape(art['category'])}</span>
            <span style="font-size: 0.78rem; color: var(--text-muted);">📅 {thai_date_card}</span>
          </div>
          <h2 class="card-title">
            <a href="articles/{art['slug']}.html">{html.escape(art['article_title'])}</a>
          </h2>
          <div class="card-price">฿{art['price']} <span style="font-size: 0.8rem; font-weight: normal; color: var(--text-muted);">(ขายแล้ว {art['sold']} ชิ้น)</span></div>
          <a href="articles/{art['slug']}.html" class="btn">อ่านรีวิวและสั่งซื้อ</a>
        </div>
      </div>
"""
        cards_html.append(card)

    index_html = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(site_title)} | รวมรีวิวสินค้าขายดี</title>
  <meta name="description" content="{html.escape(site_desc)}">
  <link rel="canonical" href="{site_url}/">
  <style>{BASE_CSS}</style>
</head>
<body>
  <header>
    <div class="header-container">
      <a href="index.html" class="logo">{html.escape(site_title)}</a>
      <div style="display: flex; align-items: center; gap: 1rem;">
        <a href="https://tautoguide.blogspot.com" target="_blank" style="font-size: 0.88rem; color: var(--primary); font-weight: 600; text-decoration: none; background: #fff1f0; padding: 0.35rem 0.75rem; border-radius: 6px; border: 1px solid #ffccc7;">🌐 เข้าชมบล็อกหลัก (tautoguide.blogspot.com) ↗</a>
      </div>
    </div>
  </header>

  <main class="container">
    <div class="hero">
      <h1>{html.escape(site_title)}</h1>
      <p>{html.escape(site_desc)}</p>
    </div>

    <div class="grid">
      {"".join(cards_html)}
    </div>
  </main>

  <footer>
    <p>© {datetime.date.today().year} {html.escape(site_title)} • อัปเดตล่าสุด: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
  </footer>
</body>
</html>
"""
    index_path = os.path.join(DOCS_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    return index_path

def build_sitemap_and_robots(articles, config):
    """สร้าง sitemap.xml และ robots.txt สำหรับ Google Search Console"""
    site_url = config.get("site_url", "https://mysite.github.io").rstrip("/")
    now_date = datetime.date.today().isoformat()

    urls = [
        f"""  <url>
    <loc>{site_url}/</loc>
    <lastmod>{now_date}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>"""
    ]

    for art in articles:
        art_date = (art.get('created_at') or '')[:10] or now_date
        art_url = f"{site_url}/articles/{art['slug']}.html"
        urls.append(f"""  <url>
    <loc>{art_url}</loc>
    <lastmod>{art_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(urls)}
</urlset>
"""
    with open(os.path.join(DOCS_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    robots_txt = f"""User-agent: *
Allow: /

Sitemap: {site_url}/sitemap.xml
"""
    with open(os.path.join(DOCS_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots_txt)

def update_website(new_articles, config):
    """อัปเดตเว็บไซต์ทั้งหมดด้วยบทความชุดใหม่"""
    init_dirs()
    existing_articles = load_site_articles()
    
    # รวมบทความใหม่ ไม่ให้ซ้ำ ID
    existing_ids = {a["id"] for a in existing_articles}
    for art in new_articles:
        if art["id"] not in existing_ids:
            existing_articles.append(art)
            existing_ids.add(art["id"])

    save_site_articles(existing_articles)

    # สร้างหน้าบทความแต่ละหน้า
    for art in existing_articles:
        build_article_page(art, config)

    # สร้างหน้าแรก และ Sitemap
    build_index_page(existing_articles, config)
    build_sitemap_and_robots(existing_articles, config)

    print(f"[*] อัปเดตเว็บไซต์ใน '{DOCS_DIR}' สำเร็จ (มีบทความทั้งหมด {len(existing_articles)} ชิ้น)")
    return len(existing_articles)
