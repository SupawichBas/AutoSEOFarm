import csv
import glob
import json
import os
import sys

HISTORY_FILE = "history.json"

def load_history():
    """โหลดประวัติสินค้าที่เคยสร้างบทความไปแล้ว"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"[!] Warning reading history: {e}")
            return set()
    return set()

def save_history(processed_ids):
    """บันทึกประวัติสินค้าที่ทำไปแล้ว"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(processed_ids), f, ensure_ascii=False, indent=2)

def find_feed_file():
    """ค้นหาไฟล์ CSV Feed ในโฟลเดอร์โปรเจกต์"""
    csv_files = glob.glob("*.csv")
    if not csv_files:
        raise FileNotFoundError("ไม่พบไฟล์ .csv ในโฟลเดอร์โปรเจกต์")
    # เลือกไฟล์ที่ใหญ่ที่สุด (ซึ่งเป็นไฟล์ Feed หลัก)
    csv_files.sort(key=os.path.getsize, reverse=True)
    return csv_files[0]

def get_next_products(batch_size=3, target_categories=None, min_sold=5):
    """ดึงสินค้าชุดใหม่จาก CSV Feed ที่ยังไม่เคยประมวลผล"""
    feed_path = find_feed_file()
    print(f"[*] กำลังอ่าน Feed จาก: {feed_path}")

    history = load_history()
    selected_products = []
    
    target_cats = set(target_categories) if target_categories else set()

    with open(feed_path, mode="r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item_id = row.get("itemid", "").strip()
            if not item_id or item_id in history:
                continue

            # ตรวจสอบหมวดหมู่
            cat1 = row.get("global_category1", "").strip()
            if target_cats and cat1 not in target_cats:
                continue

            # ตรวจสอบยอดขาย
            try:
                sold = int(float(row.get("item_sold", 0) or 0))
            except (ValueError, TypeError):
                sold = 0
            if sold < min_sold:
                continue

            # ตรวจสอบลิงก์ Affiliate
            affiliate_link = row.get("product_short link", "").strip()
            if not affiliate_link or not affiliate_link.startswith("http"):
                continue

            title = row.get("title", "").strip()
            if not title:
                continue

            price = row.get("sale_price") or row.get("price") or "0"
            image = row.get("image_link") or row.get("image_link_4") or ""

            product = {
                "id": item_id,
                "title": title,
                "price": price,
                "sold": sold,
                "category": cat1,
                "category2": row.get("global_category2", "").strip(),
                "image": image,
                "affiliate_link": affiliate_link,
                "shop_name": row.get("shop_name", "").strip()
            }
            selected_products.append(product)
            history.add(item_id)

            if len(selected_products) >= batch_size:
                break

    save_history(history)
    print(f"[*] คัดเลือกสินค้าใหม่ได้ {len(selected_products)} รายการ")
    return selected_products

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    items = get_next_products(batch_size=2)
    for p in items:
        print(f"- {p['title']} ({p['price']} บ.) -> {p['affiliate_link']}")
