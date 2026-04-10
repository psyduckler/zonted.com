#!/usr/bin/env python3
"""
Build script for zonted.com
Scans article files, generates homepage index, hub pages, sitemap, RSS feed,
and injects next/prev + share links into articles.

Usage: python3 scripts/build.py
Run from the repo root.
"""

import os
import re
import html
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://zonted.com"

FALLBACK_DATES = {
    "posts/what-is-ai-self-healing": "2026-03-29",
    "posts/veo3-vs-hailuo-minimax": "2026-03-11",
    "posts/nano-banana-vs-grok": "2026-03-14",
    "posts/best-short-form-video-services": "2026-03-01",
    "posts/ai-resilience-planning": "2026-03-27",
    "posts/ai-music-generation-comparison": "2026-03-11",
    "posts/ai-image-generation-comparison": "2026-03-11",
}

# ---------------------------------------------------------------------------
# Category assignment
# ---------------------------------------------------------------------------

def get_category(slug, title):
    title_lower = title.lower()
    slug_lower = slug.lower()
    if 'review' in slug_lower:
        return 'Reviews'
    if any(w in title_lower for w in ['vs', 'comparison', 'compared', 'showdown', 'best ai']):
        return 'Comparisons'
    if any(w in title_lower for w in ['what is', 'how to', 'guide', 'planning']):
        return 'Guides'
    if any(w in title_lower for w in ['reels', 'instagram', 'youtube', 'tiktok', 'short-form', 'video services']):
        return 'Production'
    return 'Opinion'


# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------

def extract_metadata(filepath, slug):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    head_match = re.search(r'<head[^>]*>(.*?)</head>', content, re.DOTALL | re.IGNORECASE)
    head = head_match.group(1) if head_match else content

    # Title
    title_match = re.search(r'<title>(.*?)</title>', head, re.DOTALL | re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else slug
    # Strip suffixes
    for suffix in [' — zonted.com', ' — Zonted', ' &mdash; zonted.com', ' &mdash; Zonted']:
        if title.endswith(suffix):
            title = title[:-len(suffix)]
    # Also handle HTML entity dash
    title = re.sub(r'\s*(?:—|&mdash;)\s*(?:zonted\.com|Zonted)\s*$', '', title)

    # Description
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', head, re.IGNORECASE)
    description = html.unescape(desc_match.group(1)) if desc_match else ''

    # Date from article:published_time
    date_match = re.search(r'<meta\s+property=["\']article:published_time["\']\s+content=["\'](\d{4}-\d{2}-\d{2})', head, re.IGNORECASE)
    date_str = None
    if date_match:
        date_str = date_match.group(1)
    elif slug in FALLBACK_DATES:
        date_str = FALLBACK_DATES[slug]

    # Reading time
    rt_match = re.search(r'(\d+)\s*min\s*read', content, re.IGNORECASE)
    reading_time = int(rt_match.group(1)) if rt_match else None

    category = get_category(slug, title)

    return {
        'title': html.unescape(title),
        'description': description,
        'date': date_str,
        'reading_time': reading_time,
        'slug': slug,
        'category': category,
        'filepath': filepath,
    }


def scan_articles():
    articles = []
    section_dir = os.path.join(ROOT, 'posts')
    if os.path.isdir(section_dir):
        for name in os.listdir(section_dir):
            article_dir = os.path.join(section_dir, name)
            index_file = os.path.join(article_dir, 'index.html')
            if os.path.isdir(article_dir) and os.path.isfile(index_file):
                slug = f"posts/{name}"
                meta = extract_metadata(index_file, slug)
                articles.append(meta)

    # Sort by date (newest first), articles without dates go last
    articles.sort(key=lambda a: a['date'] or '0000-00-00', reverse=True)
    return articles


# ---------------------------------------------------------------------------
# Date formatting
# ---------------------------------------------------------------------------

def format_date_short(date_str):
    """Format YYYY-MM-DD to 'Apr 9, 2026'."""
    if not date_str:
        return ''
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return dt.strftime('%b %-d, %Y')


def format_date_rfc822(date_str):
    """Format YYYY-MM-DD to RFC 822 for RSS."""
    if not date_str:
        return ''
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    # RFC 822: e.g. Wed, 09 Apr 2026 00:00:00 +0000
    return dt.strftime('%a, %d %b %Y 00:00:00 +0000')


# ---------------------------------------------------------------------------
# Entry list HTML generation
# ---------------------------------------------------------------------------

def make_entry_row(article):
    date_display = format_date_short(article['date']) if article['date'] else ''
    cat = article['category'].lower()

    return (
        f'                <li class="entry-row" data-category="{cat}">\n'
        f'                    <span class="entry-date">{date_display}</span>\n'
        f'                    <a href="/{article["slug"]}/" class="entry-title">{html.escape(article["title"])}</a>\n'
        f'                </li>'
    )


# ---------------------------------------------------------------------------
# Homepage generation
# ---------------------------------------------------------------------------

FILTER_BAR_HTML = '''            <div class="filter-bar" style="margin-bottom:16px;display:flex;gap:8px;flex-wrap:wrap;">
                <button class="filter-btn active" data-filter="all" style="font-family:'Inter',system-ui,sans-serif;font-size:0.8rem;font-weight:500;padding:4px 12px;border:1px solid var(--border);border-radius:4px;background:var(--text);color:var(--bg);cursor:pointer;">All</button>
                <button class="filter-btn" data-filter="reviews" style="font-family:'Inter',system-ui,sans-serif;font-size:0.8rem;font-weight:500;padding:4px 12px;border:1px solid var(--border);border-radius:4px;background:var(--bg);color:var(--text-muted);cursor:pointer;">Reviews</button>
                <button class="filter-btn" data-filter="comparisons" style="font-family:'Inter',system-ui,sans-serif;font-size:0.8rem;font-weight:500;padding:4px 12px;border:1px solid var(--border);border-radius:4px;background:var(--bg);color:var(--text-muted);cursor:pointer;">Comparisons</button>
                <button class="filter-btn" data-filter="guides" style="font-family:'Inter',system-ui,sans-serif;font-size:0.8rem;font-weight:500;padding:4px 12px;border:1px solid var(--border);border-radius:4px;background:var(--bg);color:var(--text-muted);cursor:pointer;">Guides</button>
                <button class="filter-btn" data-filter="production" style="font-family:'Inter',system-ui,sans-serif;font-size:0.8rem;font-weight:500;padding:4px 12px;border:1px solid var(--border);border-radius:4px;background:var(--bg);color:var(--text-muted);cursor:pointer;">Production</button>
                <button class="filter-btn" data-filter="opinion" style="font-family:'Inter',system-ui,sans-serif;font-size:0.8rem;font-weight:500;padding:4px 12px;border:1px solid var(--border);border-radius:4px;background:var(--bg);color:var(--text-muted);cursor:pointer;">Opinion</button>
            </div>'''

FILTER_JS = '''<!-- FILTER_JS_START -->
<script>
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const filter = btn.dataset.filter;
        document.querySelectorAll('.filter-btn').forEach(b => {
            b.style.background = 'var(--bg)';
            b.style.color = 'var(--text-muted)';
            b.classList.remove('active');
        });
        btn.style.background = 'var(--text)';
        btn.style.color = 'var(--bg)';
        btn.classList.add('active');
        document.querySelectorAll('.entry-row').forEach(row => {
            if (filter === 'all' || row.dataset.category === filter) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
});
</script>
<!-- FILTER_JS_END -->'''


def generate_homepage(articles):
    filepath = os.path.join(ROOT, 'index.html')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Build entry list
    rows = [make_entry_row(a) for a in articles]
    entry_html = '\n'.join(rows)

    new_block = (
        f'<!-- ENTRY_LIST_START -->\n'
        f'{FILTER_BAR_HTML}\n'
        f'            <ul class="entry-list">\n'
        f'{entry_html}\n'
        f'            </ul>\n'
        f'            <!-- ENTRY_LIST_END -->'
    )

    # Replace between markers
    content = re.sub(
        r'<!-- ENTRY_LIST_START -->.*?<!-- ENTRY_LIST_END -->',
        new_block,
        content,
        flags=re.DOTALL
    )

    # Update article count
    count = len(articles)
    content = re.sub(
        r'\d+ articles,',
        f'{count} articles,',
        content
    )

    # Inject/update filter JS before </body>
    if '<!-- FILTER_JS_START -->' in content:
        content = re.sub(
            r'<!-- FILTER_JS_START -->.*?<!-- FILTER_JS_END -->',
            FILTER_JS,
            content,
            flags=re.DOTALL
        )
    else:
        content = content.replace('</body>', f'{FILTER_JS}\n</body>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return count


# ---------------------------------------------------------------------------
# Posts hub generation
# ---------------------------------------------------------------------------

def generate_posts_hub(articles):
    filepath = os.path.join(ROOT, 'posts', 'index.html')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    rows = [make_entry_row(a) for a in articles]
    entry_html = '\n'.join(rows)

    new_block = (
        f'<!-- ENTRY_LIST_START -->\n'
        f'            <ul class="entry-list">\n'
        f'{entry_html}\n'
        f'            </ul>\n'
        f'            <!-- ENTRY_LIST_END -->'
    )

    content = re.sub(
        r'<!-- ENTRY_LIST_START -->.*?<!-- ENTRY_LIST_END -->',
        new_block,
        content,
        flags=re.DOTALL
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return len(articles)


# ---------------------------------------------------------------------------
# Sitemap generation
# ---------------------------------------------------------------------------

def generate_sitemap(articles):
    today = datetime.now().strftime('%Y-%m-%d')
    urls = []

    # Homepage
    urls.append(('/', '1.0', today))
    # Hubs
    urls.append(('/posts/', '0.8', today))
    # About
    urls.append(('/about/', '0.6', today))

    # Articles
    for a in articles:
        lastmod = a['date'] or today
        urls.append((f'/{a["slug"]}/', '0.7', lastmod))

    xml_entries = []
    for loc, priority, lastmod in urls:
        xml_entries.append(
            f'  <url>\n'
            f'    <loc>{SITE_URL}{loc}</loc>\n'
            f'    <lastmod>{lastmod}</lastmod>\n'
            f'    <priority>{priority}</priority>\n'
            f'  </url>'
        )

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(xml_entries) + '\n'
        '</urlset>\n'
    )

    filepath = os.path.join(ROOT, 'sitemap.xml')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(sitemap)

    return len(urls)


# ---------------------------------------------------------------------------
# RSS feed generation
# ---------------------------------------------------------------------------

def generate_feed(articles):
    items = []
    for a in articles:
        pub_date = format_date_rfc822(a['date']) if a['date'] else ''
        desc_escaped = html.escape(a['description'])
        link = f'{SITE_URL}/{a["slug"]}/'
        items.append(
            f'    <item>\n'
            f'      <title>{html.escape(a["title"])}</title>\n'
            f'      <link>{link}</link>\n'
            f'      <description>{desc_escaped}</description>\n'
            f'      <pubDate>{pub_date}</pubDate>\n'
            f'      <author>bernard@zonted.com (Bernard Huang)</author>\n'
            f'      <guid isPermaLink="true">{link}</guid>\n'
            f'    </item>'
        )

    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        '  <channel>\n'
        '    <title>Zonted</title>\n'
        f'    <link>{SITE_URL}/</link>\n'
        '    <description>I test AI tools so you don\'t have to. Honest reviews, real data, and opinions from someone who actually builds with this stuff.</description>\n'
        '    <language>en-us</language>\n'
        f'    <lastBuildDate>{format_date_rfc822(datetime.now().strftime("%Y-%m-%d"))}</lastBuildDate>\n'
        f'    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml" />\n'
        + '\n'.join(items) + '\n'
        '  </channel>\n'
        '</rss>\n'
    )

    filepath = os.path.join(ROOT, 'feed.xml')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(feed)

    return len(items)


# ---------------------------------------------------------------------------
# Next/prev + share links injection
# ---------------------------------------------------------------------------

def strip_nav_links(articles):
    """Remove share-on-X + next/prev nav links from all articles."""
    count = 0
    for article in articles:
        filepath = article['filepath']
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if '<!-- NAV_LINKS_START -->' in content and '<!-- NAV_LINKS_END -->' in content:
            content = re.sub(
                r'\n*<!-- NAV_LINKS_START -->.*?<!-- NAV_LINKS_END -->\n*',
                '\n',
                content,
                flags=re.DOTALL
            )
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            count += 1

    return count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    articles = scan_articles()
    print(f"Found {len(articles)} articles")

    n = generate_homepage(articles)
    print(f"Generated index.html ({n} entries)")

    n = generate_posts_hub(articles)
    print(f"Generated posts/index.html ({n} entries)")

    n = generate_sitemap(articles)
    print(f"Generated sitemap.xml ({n} URLs)")

    n = generate_feed(articles)
    print(f"Generated feed.xml ({n} items)")

    n = strip_nav_links(articles)
    print(f"Stripped nav links from {n} articles")


if __name__ == '__main__':
    main()
