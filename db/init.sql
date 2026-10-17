-- เปิดใช้งานส่วนเสริมสำหรับสร้าง UUID อัตโนมัติ
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. ตารางจัดการคีย์เวิร์ดและหมวดหมู่ (สำหรับหน้า Angular Dashboard)
CREATE TABLE IF NOT EXISTS keywords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,
    min_price NUMERIC(12, 2) DEFAULT 490.00,
    min_sold INT DEFAULT 5,
    require_mall BOOLEAN DEFAULT TRUE,
    priority INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    last_scraped_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. ตารางเก็บข้อมูลสินค้า Affiliate (Products)
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword_id UUID REFERENCES keywords(id) ON DELETE SET NULL,
    platform VARCHAR(50) NOT NULL DEFAULT 'SHOPEE',
    platform_item_id VARCHAR(100) NOT NULL,
    shop_id VARCHAR(100),
    product_title TEXT NOT NULL,
    category VARCHAR(100),
    price NUMERIC(12, 2) NOT NULL DEFAULT 0,
    sold_count INT NOT NULL DEFAULT 0,
    image_url TEXT,
    origin_url TEXT,
    affiliate_link TEXT NOT NULL,
    affiliate_id VARCHAR(50) NOT NULL DEFAULT '15316300462',
    sub_id VARCHAR(100) DEFAULT 'tautoguide',
    status VARCHAR(30) NOT NULL DEFAULT 'GENERATED', -- NEW, QUEUED_FOR_AI, GENERATED, REJECTED
    raw_metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_platform_item UNIQUE (platform, platform_item_id)
);

-- 3. ตารางเก็บเนื้อหาบทความ SEO ที่สร้างจาก AI (Articles)
CREATE TABLE IF NOT EXISTS articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    slug VARCHAR(255) NOT NULL UNIQUE,
    article_title TEXT NOT NULL,
    summary TEXT,
    content_markdown TEXT NOT NULL,
    content_html TEXT,
    seo_tags TEXT[],
    qa_passed BOOLEAN NOT NULL DEFAULT TRUE,
    qa_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. ตารางบัญชี Blogger & การควบคุมโควต้า (Blogger Accounts)
CREATE TABLE IF NOT EXISTS blogger_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    blog_id VARCHAR(100) NOT NULL UNIQUE,
    blog_name VARCHAR(255) NOT NULL,
    blog_url TEXT NOT NULL,
    client_credentials_json TEXT,
    daily_quota_limit INT NOT NULL DEFAULT 10,
    daily_quota_used INT NOT NULL DEFAULT 0,
    quota_reset_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. ตารางคิวงานโพสต์บทความอัตโนมัติ (Publish Queue)
CREATE TABLE IF NOT EXISTS publish_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    blog_account_id UUID REFERENCES blogger_accounts(id) ON DELETE CASCADE,
    target_platform VARCHAR(50) NOT NULL DEFAULT 'GITHUB_AND_BLOGGER',
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    -- สถานะ: PENDING, PROCESSING, PUBLISHED, RATE_LIMITED, FAILED, CANCELLED
    scheduled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    locked_at TIMESTAMPTZ,
    locked_by VARCHAR(100),
    published_at TIMESTAMPTZ,
    retry_count INT NOT NULL DEFAULT 0,
    max_retries INT NOT NULL DEFAULT 3,
    next_retry_at TIMESTAMPTZ,
    blogger_post_id VARCHAR(100),
    published_url TEXT,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_article_per_blog UNIQUE (article_id, blog_account_id)
);

-- 6. ตารางประวัติการทำงานของคิวและบอท (Queue Logs)
CREATE TABLE IF NOT EXISTS queue_logs (
    id BIGSERIAL PRIMARY KEY,
    queue_id UUID REFERENCES publish_queue(id) ON DELETE CASCADE,
    worker_name VARCHAR(100),
    log_level VARCHAR(20) NOT NULL DEFAULT 'INFO',
    action VARCHAR(50) NOT NULL,
    http_status_code INT,
    message TEXT NOT NULL,
    response_payload JSONB,
    execution_ms INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. ตารางจดจำลิ้งก์สินค้าที่ผู้ใช้ใส่ไว้รอรันสคริปต์ทีหลัง (Saved Links)
CREATE TABLE IF NOT EXISTS saved_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_url TEXT NOT NULL,
    affiliate_link TEXT NOT NULL,
    note TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'SAVED', -- SAVED, PROCESSED
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- INDEXES สำหรับเร่งความเร็ว Worker Queue และหน้า Angular Dashboard
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_publish_queue_poll 
    ON publish_queue (scheduled_at ASC, status) 
    WHERE status IN ('PENDING', 'RATE_LIMITED');

CREATE INDEX IF NOT EXISTS idx_products_status_category ON products (status, category);
CREATE INDEX IF NOT EXISTS idx_queue_logs_queue_id_created ON queue_logs (queue_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_queue_logs_created_at ON queue_logs (created_at DESC);
