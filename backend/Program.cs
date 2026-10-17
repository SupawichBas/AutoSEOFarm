using System.Text.RegularExpressions;
using Dapper;
using Npgsql;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
        policy.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod());
});

var connString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? "Host=postgres-db;Port=5432;Database=affiliate_seo_db;Username=affiliate_admin;Password=StrongPass123!";

const string DefaultAffiliateId = "15316300462";
const string DefaultSubId = "tautoguide";

var app = builder.Build();
app.UseCors();

// 1. Health Check
app.MapGet("/health", () => Results.Ok(new { status = "healthy", timestamp = DateTime.UtcNow }));

// 2. Dashboard Summary Stats
app.MapGet("/api/stats", async () =>
{
    await using var conn = new NpgsqlConnection(connString);
    var sql = @"
        SELECT
            (SELECT COUNT(*) FROM products) AS total_products,
            (SELECT COUNT(*) FROM saved_links WHERE status = 'SAVED') AS saved_links_count,
            (SELECT COUNT(*) FROM publish_queue WHERE status = 'PUBLISHED') AS published_count,
            (SELECT COUNT(*) FROM publish_queue WHERE status = 'PENDING') AS pending_count,
            (SELECT COUNT(*) FROM keywords WHERE is_active = TRUE) AS active_keywords;
    ";
    var stats = await conn.QueryFirstAsync(sql);
    return Results.Ok(stats);
});

// 3. Get Saved Links (รายการลิ้งก์ที่ใส่ไว้รอรันสคริปต์ทีหลัง)
app.MapGet("/api/saved-links", async () =>
{
    await using var conn = new NpgsqlConnection(connString);
    var items = await conn.QueryAsync("SELECT * FROM saved_links ORDER BY created_at DESC;");
    return Results.Ok(items);
});

// 4. Add Saved Link (แปลงลิ้งก์เป็น Affiliate ของคุณ + จำลิ้งก์ไว้รอรันสคริปต์อย่างเดียว ไม่เจนบทความเอง)
app.MapPost("/api/saved-links", async (SaveLinkDto dto) =>
{
    if (string.IsNullOrWhiteSpace(dto.RawUrl))
        return Results.BadRequest(new { error = "กรุณาวางลิ้งก์สินค้า Shopee" });

    var rawUrl = dto.RawUrl.Trim();
    var originMatch = Regex.Match(rawUrl, @"origin_link=([^&]+)");
    if (originMatch.Success)
    {
        rawUrl = Uri.UnescapeDataString(originMatch.Groups[1].Value);
    }

    string cleanOriginUrl = rawUrl.Split('?')[0];
    var m1 = Regex.Match(rawUrl, @"shopee\.co\.th/(?:product|opaanlp)/(\d+)/(\d+)");
    var m2 = Regex.Match(rawUrl, @"-i\.(\d+)\.(\d+)");

    if (m1.Success)
    {
        cleanOriginUrl = $"https://shopee.co.th/product/{m1.Groups[1].Value}/{m1.Groups[2].Value}";
    }
    else if (m2.Success)
    {
        cleanOriginUrl = $"https://shopee.co.th/product/{m2.Groups[1].Value}/{m2.Groups[2].Value}";
    }

    string note = dto.Note?.Trim() ?? "";
    if (string.IsNullOrWhiteSpace(note))
    {
        try
        {
            var uri = new Uri(rawUrl);
            var seg = Uri.UnescapeDataString(uri.AbsolutePath.Trim('/'));
            seg = Regex.Replace(seg, @"-i\.\d+\.\d+$", "");
            if (!seg.StartsWith("product/") && !seg.StartsWith("opaanlp/") && seg != "an_redir" && seg.Length > 3)
                note = seg.Replace("-", " ");
        }
        catch { }
    }
    if (string.IsNullOrWhiteSpace(note))
        note = cleanOriginUrl;

    string encodedOrigin = Uri.EscapeDataString(cleanOriginUrl);
    string myAffiliateLink = $"https://shope.ee/an_redir?origin_link={encodedOrigin}&affiliate_id={DefaultAffiliateId}&sub_id={DefaultSubId}";

    await using var conn = new NpgsqlConnection(connString);
    var saved = await conn.QueryFirstAsync(@"
        INSERT INTO saved_links (raw_url, affiliate_link, note, status)
        VALUES (@cleanOriginUrl, @myAffiliateLink, @note, 'SAVED')
        RETURNING *;
    ", new { cleanOriginUrl, myAffiliateLink, note });

    return Results.Ok(saved);
});

// 5. Delete Saved Link
app.MapDelete("/api/saved-links/{id:guid}", async (Guid id) =>
{
    await using var conn = new NpgsqlConnection(connString);
    await conn.ExecuteAsync("DELETE FROM saved_links WHERE id = @id", new { id });
    return Results.Ok(new { deleted = true });
});

// 6. Get Publish Queue (with Product & Article details)
app.MapGet("/api/queue", async (string? status) =>
{
    await using var conn = new NpgsqlConnection(connString);
    var sql = @"
        SELECT 
            pq.id,
            pq.status,
            pq.scheduled_at,
            pq.published_at,
            pq.published_url,
            pq.retry_count,
            a.article_title,
            a.slug,
            p.platform_item_id,
            p.product_title,
            p.category,
            p.price,
            p.sold_count,
            p.image_url,
            p.affiliate_link,
            p.affiliate_id
        FROM publish_queue pq
        JOIN articles a ON pq.article_id = a.id
        JOIN products p ON a.product_id = p.id
        WHERE (@status IS NULL OR pq.status = @status)
        ORDER BY 
            CASE WHEN pq.status = 'PENDING' THEN 0 ELSE 1 END,
            pq.scheduled_at DESC
        LIMIT 100;
    ";
    var items = await conn.QueryAsync(sql, new { status });
    return Results.Ok(items);
});

// 7. Delete a Queue Item
app.MapDelete("/api/queue/{id:guid}", async (Guid id) =>
{
    await using var conn = new NpgsqlConnection(connString);
    await conn.ExecuteAsync(@"
        DELETE FROM products
        WHERE id IN (
            SELECT a.product_id FROM publish_queue pq
            JOIN articles a ON pq.article_id = a.id
            WHERE pq.id = @id
        );
    ", new { id });
    return Results.Ok(new { deleted = true });
});

// 8. Get Keywords
app.MapGet("/api/keywords", async () =>
{
    await using var conn = new NpgsqlConnection(connString);
    var items = await conn.QueryAsync("SELECT * FROM keywords ORDER BY priority ASC, created_at DESC;");
    return Results.Ok(items);
});

// 9. Add Keyword
app.MapPost("/api/keywords", async (KeywordDto dto) =>
{
    await using var conn = new NpgsqlConnection(connString);
    var sql = @"
        INSERT INTO keywords (keyword, category, min_price, min_sold, require_mall, priority, is_active)
        VALUES (@Keyword, @Category, @MinPrice, @MinSold, true, 1, true)
        ON CONFLICT (keyword) DO UPDATE SET category = EXCLUDED.category, is_active = true
        RETURNING *;
    ";
    var item = await conn.QueryFirstAsync(sql, dto);
    return Results.Ok(item);
});

// 10. Delete Keyword
app.MapDelete("/api/keywords/{id:guid}", async (Guid id) =>
{
    await using var conn = new NpgsqlConnection(connString);
    await conn.ExecuteAsync("DELETE FROM keywords WHERE id = @id", new { id });
    return Results.Ok(new { deleted = true });
});

// 11. Get Queue Logs
app.MapGet("/api/logs", async () =>
{
    await using var conn = new NpgsqlConnection(connString);
    var items = await conn.QueryAsync(@"
        SELECT l.*, a.article_title
        FROM queue_logs l
        LEFT JOIN publish_queue pq ON l.queue_id = pq.id
        LEFT JOIN articles a ON pq.article_id = a.id
        ORDER BY l.created_at DESC
        LIMIT 50;
    ");
    return Results.Ok(items);
});

app.Run();

public record KeywordDto(string Keyword, string Category, decimal MinPrice = 490, int MinSold = 5);
public record SaveLinkDto(string RawUrl, string? Note = null);
