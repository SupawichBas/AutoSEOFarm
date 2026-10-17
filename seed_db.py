import json
import os
import subprocess
import sys
import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def sql_str(val):
    if val is None:
        return "NULL"
    s = str(val).replace("'", "''")
    return f"'{s}'"

def generate_seed_sql():
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    with open(os.path.join("docs", "data", "articles.json"), "r", encoding="utf-8") as f:
        live_articles = json.load(f)

    with open("article_queue.json", "r", encoding="utf-8") as f:
        queued_articles = json.load(f)

    sql_lines = [
        "BEGIN;",
        "-- 1. Insert Blogger Account",
        """INSERT INTO blogger_accounts (blog_id, blog_name, blog_url, daily_quota_limit, daily_quota_used, is_active)
VALUES ('3662006705330094237', 'TechAuto Guide', 'https://tautoguide.blogspot.com/', 10, 0, TRUE)
ON CONFLICT (blog_id) DO NOTHING;"""
    ]

    # 2. Insert Keywords from target_categories
    categories = config.get("target_categories", [])
    for idx, cat in enumerate(categories):
        sql_lines.append(f"""INSERT INTO keywords (keyword, category, min_price, min_sold, require_mall, priority, is_active)
VALUES ({sql_str(cat)}, {sql_str(cat)}, 490.00, 5, TRUE, {idx+1}, TRUE)
ON CONFLICT (keyword) DO NOTHING;""")

    # Helper to insert product + article + queue
    def add_item_sql(art, is_published, queue_index=0):
        item_id = str(art.get("id", ""))
        prod_title = art.get("product_title", "")
        cat = art.get("category", "General")
        try:
            price = float(str(art.get("price", 0)).replace(",", ""))
        except Exception:
            price = 0.0
        try:
            sold = int(str(art.get("sold", 0)).replace(",", ""))
        except Exception:
            sold = 0
        img = art.get("image", "")
        aff_link = art.get("affiliate_link", "")
        slug = art.get("slug", f"item-{item_id}")[:250]
        art_title = art.get("article_title", prod_title)
        summary = art.get("summary", "")
        md = art.get("content_markdown", "")
        created_at = art.get("created_at") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if is_published:
            q_status = "PUBLISHED"
            sched_at = f"{created_at}+07"
            pub_at = f"'{created_at}+07'"
            pub_url = sql_str(f"https://supawichbas.github.io/ShopeeAutoSEOFarm/articles/{slug}.html")
            action = "PUBLISHED_LIVE"
            msg = f"เผยแพร่บทความสำเร็จบน GitHub Pages & ระบบ SEO ({created_at})"
        else:
            q_status = "PENDING"
            # คำนวณวันปล่อยล่วงหน้า วันละ 10 ชิ้น
            days_offset = (queue_index // 10) + 1
            slot_idx = queue_index % 10
            peak_hours = [(8,0),(9,30),(11,0),(12,30),(14,0),(15,30),(17,0),(18,30),(20,0),(21,30)]
            h, m = peak_hours[slot_idx]
            target_dt = datetime.date.today() + datetime.timedelta(days=days_offset)
            sched_str = f"{target_dt.isoformat()} {h:02d}:{m:02d}:00+07"
            sched_at = sched_str
            pub_at = "NULL"
            pub_url = "NULL"
            action = "ENQUEUED_DRIP"
            msg = f"เข้าคิวรอปล่อยอัตโนมัติ รอบวันที่ {target_dt.isoformat()} เวลา {h:02d}:{m:02d} น."

        sql_lines.append(f"""
-- Item {item_id}
WITH ins_prod AS (
    INSERT INTO products (platform, platform_item_id, product_title, category, price, sold_count, image_url, affiliate_link, affiliate_id, sub_id, status)
    VALUES ('SHOPEE', {sql_str(item_id)}, {sql_str(prod_title)}, {sql_str(cat)}, {price}, {sold}, {sql_str(img)}, {sql_str(aff_link)}, '15316300462', 'tautoguide', 'GENERATED')
    ON CONFLICT (platform, platform_item_id) DO UPDATE SET updated_at = NOW()
    RETURNING id
),
ins_art AS (
    INSERT INTO articles (product_id, slug, article_title, summary, content_markdown, qa_passed)
    SELECT id, {sql_str(slug)}, {sql_str(art_title)}, {sql_str(summary)}, {sql_str(md)}, TRUE FROM ins_prod
    ON CONFLICT (slug) DO UPDATE SET updated_at = NOW()
    RETURNING id
),
ins_queue AS (
    INSERT INTO publish_queue (article_id, blog_account_id, status, scheduled_at, published_at, published_url)
    SELECT ins_art.id, b.id, {sql_str(q_status)}, {sql_str(sched_at)}, {pub_at}, {pub_url}
    FROM ins_art CROSS JOIN (SELECT id FROM blogger_accounts WHERE blog_id = '3662006705330094237' LIMIT 1) b
    ON CONFLICT (article_id, blog_account_id) DO UPDATE SET status = EXCLUDED.status
    RETURNING id
)
INSERT INTO queue_logs (queue_id, worker_name, log_level, action, http_status_code, message, execution_ms)
SELECT id, 'shopee-auto-seo-bot', 'INFO', {sql_str(action)}, 200, {sql_str(msg)}, 145
FROM ins_queue;
""")

    for art in live_articles:
        add_item_sql(art, is_published=True)

    for idx, art in enumerate(queued_articles):
        add_item_sql(art, is_published=False, queue_index=idx)

    sql_lines.append("COMMIT;")

    seed_path = os.path.join("db", "seed_data.sql")
    with open(seed_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_lines))
    print(f"[✓] สร้างไฟล์ SQL Seed สำเร็จ: {seed_path} (Live {len(live_articles)} + Queue {len(queued_articles)})")

if __name__ == "__main__":
    generate_seed_sql()
