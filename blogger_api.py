import os
import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

SCOPES = ['https://www.googleapis.com/auth/blogger']
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'

def get_blogger_service():
    """เชื่อมต่อกับ Google Blogger API โดยเก็บ Token ไว้ใช้ซ้ำได้ตลอดไป"""
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"[!] Warning reading token: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[*] กำลังรีเฟรช Token ของ Google...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(f"ไม่พบไฟล์ {CLIENT_SECRET_FILE} ในโฟลเดอร์โปรเจกต์")
            
            print("\n" + "="*60)
            print("🔑 กำลังเปิดเบราว์เซอร์เพื่อให้คุณเข้าสู่ระบบ Google 1 ครั้ง...")
            print("="*60 + "\n")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())

    service = build('blogger', 'v3', credentials=creds)
    return service

def get_target_blog(service, blog_name_hint="Shopee Review"):
    """ค้นหา ID ของบล็อกเป้าหมาย"""
    blogs_result = service.blogs().listByUser(userId='self').execute()
    items = blogs_result.get('items', [])
    if not items:
        raise ValueError("ไม่พบบล็อกในบัญชี Google นี้ กรุณาสร้างบล็อกที่ blogger.com ก่อน")

    for b in items:
        if blog_name_hint.lower() in b['name'].lower():
            return b

    # หากไม่เจอชื่อที่ระบุ ให้เลือกบล็อกแรก
    return items[0]

def publish_to_blogger(article, blog_id=None, service=None):
    """ส่งบทความขึ้น Blogger ทันทีแบบอัตโนมัติ"""
    if not service:
        service = get_blogger_service()

    if not blog_id:
        target_blog = get_target_blog(service)
        blog_id = target_blog['id']

    # เนื้อหา HTML จาก article
    from blogger_exporter import BLOGGER_DIR
    html_file = os.path.join(BLOGGER_DIR, f"{article['slug']}.html")
    
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
        body_content = raw_content.split("-->\n\n", 1)[-1] if "-->\n\n" in raw_content else raw_content
    else:
        import markdown
        body_content = markdown.markdown(article['content_markdown'], extensions=['extra'])

    post_body = {
        'title': article['article_title'],
        'content': body_content,
        'labels': [article['category'], 'Shopee', 'รีวิวสินค้า']
    }
    if article.get('image'):
        post_body['images'] = [{'url': article['image']}]


    try:
        post = service.posts().insert(blogId=blog_id, body=post_body, isDraft=False).execute()
        print(f"[✓] โพสต์ขึ้น Blogger สำเร็จ: {post.get('url')}")
        return post.get('url')
    except Exception as e:
        print(f"[!] ผิดพลาดในการโพสต์ขึ้น Blogger: {e}")
        return None

if __name__ == "__main__":
    print("[*] ทดสอบเชื่อมต่อ Blogger API...")
    try:
        service = get_blogger_service()
        blog = get_target_blog(service)
        print(f"[✓] เชื่อมต่อสำเร็จ! บล็อกที่พบ: {blog['name']} (ID: {blog['id']})")
        print(f"[✓] URL บล็อก: {blog['url']}")
    except Exception as e:
        print(f"[!] Error: {e}")
