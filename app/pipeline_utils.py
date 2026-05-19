"""Pure helper functions for the scrape→classify pipeline.

These have no GUI/IO dependencies so they can be unit-tested and reused
from a future CLI or scheduled-task entry point. The GUI's
ScraperFrame._run_scrape glues these together with progress callbacks
and DB writes; nothing else should be needed to run the pipeline
headless.
"""
from __future__ import annotations

import logging
from typing import Optional

log = logging.getLogger(__name__)


# Source decoration suffixes that scrapers/search engines append to
# titles. Stripped before fuzzy title dedup so 'Foo - Reddit' and
# 'Foo - r/sysadmin' collide as duplicates.
TITLE_SUFFIXES = [
    " - reddit", " : r/", " on reddit",
    " | atlassian", " - atlassian",
    " - hubspot", " | hubspot", " - hubspot community",
    " - stack overflow", " - stackoverflow",
    " - github", " · github", " · issue", " - issue",
    " - shopify community", " | shopify",
    " - woocommerce", " | woocommerce",
    " - wordpress", " | wordpress.org",
    " - dev community", " - dev.to",
    " - spiceworks", " - quora",
    " - microsoft community", " | techcommunity",
    " - airtable community", " - zapier community",
    " - notion", " - clickup", " - asana",
    " - trustpilot", " - g2.com", " - capterra",
    " - apple developer", " - apple community",
    " - bigcommerce community",
]

# Status prefixes — stripped so 'Foo' and '[SOLVED] Foo' dedup
TITLE_PREFIXES = (
    "[solved]", "[fixed]", "[resolved]", "[help]",
    "solved:", "fixed:", "resolved:", "help:",
)

# Reddit subdomain variants that all serve the same content
REDDIT_SUBDOMAIN_VARIANTS = (
    "old.reddit.com", "np.reddit.com",
    "i.reddit.com", "m.reddit.com",
)


def normalize_url(url: str) -> str:
    """Normalize a URL for cross-scraper deduplication.

    Handles common variants that scrapers may return for the same post:
    - Reddit subdomains (www. / old. / np. / m. / bare) → www.reddit.com
    - Trailing slashes
    - URL fragments (#comment-123) and tracking query strings
    - Mixed case in hostname

    Args:
        url: any URL string, possibly empty.

    Returns:
        Lowercase URL with fragments/query stripped and reddit subdomains
        normalized. Empty string if input is empty.
    """
    if not url:
        return ""
    url = url.strip().lower()
    # Drop fragment and query string
    for sep in ("#", "?"):
        if sep in url:
            url = url.split(sep, 1)[0]
    # Drop trailing slash
    url = url.rstrip("/")
    # Normalize reddit subdomains
    for variant in REDDIT_SUBDOMAIN_VARIANTS:
        if variant in url:
            url = url.replace(variant, "www.reddit.com")
    if "://reddit.com/" in url:
        url = url.replace("://reddit.com/", "://www.reddit.com/")
    return url


def normalize_title_for_dedup(title: str) -> str:
    """Normalize a post title for fuzzy duplicate detection.

    Strips source-site decorations ('- Reddit', '| Atlassian', etc.) and
    status prefixes ('[SOLVED]', 'fixed:', etc.). Returns the first 50
    characters of the cleaned, lowercased title so near-duplicate posts
    from different scrapers collide on the same key.
    """
    if not title:
        return ""
    raw = title.lower().strip()
    # Strip status prefixes
    for prefix in TITLE_PREFIXES:
        if raw.startswith(prefix):
            raw = raw[len(prefix):].strip()
            break
    # Strip source suffixes (only first match wins)
    for suffix in TITLE_SUFFIXES:
        if suffix in raw:
            raw = raw[:raw.index(suffix)]
            break
    return raw[:50]


def dedup_cross_scraper(posts: list[dict]) -> tuple[list[dict], int]:
    """Remove duplicate posts that came from multiple scrapers.

    Dedup is two-pass:
    1. By normalized URL (catches same post under different reddit subdomains
       or with/without tracking query strings).
    2. By fuzzy-normalized title prefix (catches same post returned by
       different search engines with slightly different decorations).

    Args:
        posts: list of post dicts with at minimum 'url' and 'title' keys.

    Returns:
        (deduped_posts, count_removed) tuple. deduped_posts preserves
        the input order of unique entries.
    """
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    deduped: list[dict] = []
    for p in posts:
        url_key = normalize_url(p.get("url", ""))
        title_key = normalize_title_for_dedup(p.get("title", ""))
        if url_key in seen_urls:
            continue
        if title_key and title_key in seen_titles:
            continue
        seen_urls.add(url_key)
        if title_key:
            seen_titles.add(title_key)
        deduped.append(p)
    return deduped, len(posts) - len(deduped)


def search_lead_text(lead: dict, query: str) -> bool:
    """Return True if `query` (case-insensitive) appears in any searchable
    field of the lead (title, content, summary, solution_approach, notes).

    Used by the leads_frame search box. Pulled out as a pure function
    so the same predicate can be reused for filtered CSV export and
    any future API consumer.
    """
    if not query:
        return True
    q = query.strip().lower()
    if not q:
        return True
    for field in ("title", "content", "summary", "solution_approach", "notes"):
        val = lead.get(field) or ""
        if q in val.lower():
            return True
    return False
