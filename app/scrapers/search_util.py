"""
Shared search utility for all scrapers.
Uses DuckDuckGo (via ddgs package) as primary search engine with junk filtering.

Author: Howell Brady | Origin: BonnieTheDog420
"""

import re
import time
import random
import logging
import threading

log = logging.getLogger(__name__)

# Global rate limiter — prevents DDG from blocking us across all scrapers
_last_search_time = 0.0
_search_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Junk filters — skip results that will never be useful leads
# ---------------------------------------------------------------------------

JUNK_DOMAINS = {
    # Reference / dictionary / encyclopedia
    "wikipedia.org", "dictionary.com", "merriam-webster.com",
    "cambridge.org/dictionary", "wiktionary.org", "britannica.com",
    "investopedia.com", "oxfordlearnersdictionaries.com",
    "englishpage.com", "wordreference.com", "ldoceonline.com",
    "grammarly.com", "englishclub.com", "langeek.co",
    # Social / media / shopping
    "youtube.com", "tiktok.com", "pinterest.com",
    "amazon.com", "ebay.com", "etsy.com", "airbnb.com",
    "facebook.com/login", "linkedin.com/login", "twitter.com/login",
    # Ad / tracking URLs
    "bing.com/aclick", "bing.com/ck/a",
    # SEO / link-checker tools (false positives for "broken" queries)
    "brokenlinkcheck.com", "dnschecker.org", "seojuice.com",
    "ahrefs.com", "semrush.com", "moz.com/link-explorer",
    "linksman.io", "uptek.com", "deadlinkchecker.com",
    "sitechecker.pro", "drlinkcheck.com",
    # Stock / finance (false positives for company name queries)
    "finance.yahoo.com", "fool.com", "marketwatch.com",
    "businesswire.com", "prnewswire.com",
    # Tech blog / general troubleshooting / vendor marketing (not forums)
    "howtogeek.com", "makeuseof.com", "lifehacker.com",
    "pcmag.com", "techradar.com", "tomsguide.com",
    "cloudwards.net", "comparitech.com",
    "gearset.com", "zapier.com/blog", "hubspot.com/blog",
    "salesforce.com/blog", "atlassian.com/blog",
    # Chinese / non-English sites
    "zhihu.com", "baidu.com", "csdn.net",
    # Status / monitoring (outage reports, not fixable problems)
    "downdetector.com", "isitdownrightnow.com", "outage.report",
    "status.io", "statuspage.io",
    # Job boards (not complaints)
    "indeed.com", "glassdoor.com", "ziprecruiter.com",
    # Course / training / how-to sites
    "udemy.com", "coursera.org", "pluralsight.com",
    "wikihow.com", "geeksforgeeks.org", "lifewire.com",
    "business.com/hr", "business.com/crm",  # generic how-to articles
    # App stores (not forums)
    "play.google.com", "apps.apple.com",
}

JUNK_TITLE_PATTERNS = re.compile(
    r"^(log ?in|sign ?in|sign ?up|create account|pricing|about us|"
    r"contact us|home ?page|wikipedia|definition|meaning|"
    r"what is .{0,20}\?$|"
    r"get help with|welcome to|getting started|"
    r"troubleshooting \|"
    r"|is .{0,30} down\?"  # status check pages like "Is Xero down?"
    r"|current outages"
    r"|server status)",  # category/index pages like "Troubleshooting | Zapier"
    re.IGNORECASE,
)


def _is_junk(url, title):
    """Filter out results that will never be useful leads."""
    url_lower = url.lower()
    title_lower = title.lower()

    # Skip ad/tracking URLs
    if "bing.com/aclick" in url_lower or "bing.com/ck/a" in url_lower:
        return True

    # Skip junk domains
    for domain in JUNK_DOMAINS:
        if domain in url_lower:
            return True

    # Skip homepage-level URLs (no path beyond /)
    stripped = url_lower.rstrip("/")
    if stripped.count("/") <= 2:  # https://domain.com = 2 slashes
        return True

    # Skip junk title patterns
    if JUNK_TITLE_PATTERNS.search(title_lower):
        return True

    # Skip marketing/product pages
    marketing_signals = ["pricing", "features", "get started", "free trial", "demo"]
    if any(s in title_lower for s in marketing_signals):
        return True

    # Skip product launches / self-promotion (not complaints)
    promo_signals = ["show hn:", "launch hn:", "just launched", "introducing ",
                     "we built", "i built", "now available"]
    if any(s in title_lower for s in promo_signals):
        return True

    # Skip SEO troubleshooting articles (not real complaints)
    if re.search(r"fix .{3,30} in \d+ ?(steps?|ways?|minutes?)", title_lower):
        return True
    if re.search(r"how to fix .{3,30} \[?(solved|fixed|guide|2024|2025|2026)", title_lower):
        return True

    # Skip already-solved community posts
    if title_lower.startswith("solved:") or title_lower.startswith("[solved]"):
        return True

    # Skip forum category/index pages (not actual posts)
    category_signals = [
        "help and faq", "help center", "knowledge base",
        "ask your questions here", "customer service",
    ]
    if any(s in title_lower for s in category_signals):
        return True

    # Skip official documentation / knowledge base URLs (not user complaints)
    doc_url_patterns = [
        "/hc/en-us/articles/",  # Zendesk help center articles
        "/hc/en-us/categories/",
        "knowledge.hubspot.com",
        "help.salesforce.com/s/",
        "docs.github.com",
        "developer.zendesk.com",
        "developers.cloudflare.com",
        "learn.microsoft.com",
        "docs.aws.amazon.com",
        "docs.digitalocean.com",
        "support.google.com/",
        "support.microsoft.com/",
        "support.apple.com/",
        "/documentation/",
        "/api-reference/",
        "/developer-guide/",
    ]
    if any(p in url_lower for p in doc_url_patterns):
        return True

    return False


# ---------------------------------------------------------------------------
# DuckDuckGo search via ddgs package
# ---------------------------------------------------------------------------

def _rate_limit():
    """Global rate limiter — ensures minimum 0.6s between DDG searches."""
    global _last_search_time
    with _search_lock:
        now = time.time()
        elapsed = now - _last_search_time
        if elapsed < 0.6:
            time.sleep(0.6 - elapsed + random.uniform(0, 0.2))
        _last_search_time = time.time()


def ddg_search(query, count=10):
    """Search DuckDuckGo and return filtered results.

    Uses the ddgs package which handles DDG's API properly.
    Supports site: operator (unlike Bing HTML scraping).
    Filters out ads, junk domains, homepages, and marketing pages.

    Returns:
        List of dicts with keys: title, content, url
    """
    _rate_limit()
    results = []
    try:
        from ddgs import DDGS
        ddgs = DDGS()
        raw = list(ddgs.text(query, max_results=min(count + 5, 30)))

        for item in raw:
            url = item.get("href", "")
            title = item.get("title", "")
            snippet = item.get("body", "")

            if not url or not url.startswith("http"):
                continue

            if _is_junk(url, title):
                continue

            # Skip very short/empty snippets
            if len(snippet) < 30 and len(title) < 20:
                continue

            results.append({
                "title": title,
                "content": snippet,
                "url": url,
            })

            if len(results) >= count:
                break

    except ImportError:
        log.warning("ddgs package not installed — run: pip install ddgs")
    except Exception as exc:
        log.debug("DDG search error for query '%s': %s", query[:50], exc)
        # Retry once after a longer delay
        if "Ratelimit" in str(exc) or "429" in str(exc):
            time.sleep(2 + random.uniform(0, 1))
            try:
                from ddgs import DDGS
                ddgs = DDGS()
                raw = list(ddgs.text(query, max_results=min(count, 15)))
                for item in raw:
                    url = item.get("href", "")
                    title = item.get("title", "")
                    snippet = item.get("body", "")
                    if not url or not url.startswith("http"):
                        continue
                    if _is_junk(url, title):
                        continue
                    if len(snippet) < 30 and len(title) < 20:
                        continue
                    results.append({"title": title, "content": snippet, "url": url})
                    if len(results) >= count:
                        break
            except Exception:
                pass

    return results


# ---------------------------------------------------------------------------
# Multi-query search aggregator (used by all domain-specific scrapers)
# ---------------------------------------------------------------------------

def multi_domain_search(queries, source_name="Web", limit=50, url_filter=None, delay=0.8):
    """Run multiple search queries via DuckDuckGo, filter junk, deduplicate.

    Args:
        queries: List of search query strings (site: operator IS supported)
        source_name: Default source label
        limit: Max total results
        url_filter: Optional function(url) -> source_name or None
        delay: Seconds between queries to avoid rate limiting

    Returns:
        Deduplicated list of post dicts with real URLs
    """
    all_posts = []
    per_query = max(5, limit // max(len(queries), 1))

    for q in queries:
        raw = ddg_search(q, count=per_query)

        for item in raw:
            real_url = item["url"]

            if url_filter:
                label = url_filter(real_url)
                if label is None:
                    continue
                source = label
            else:
                source = source_name

            all_posts.append({
                "source": source,
                "title": item["title"],
                "content": item["content"],
                "url": real_url,
                "author": "unknown",
            })

        if delay > 0:
            time.sleep(delay + random.uniform(0, 0.3))

    # Deduplicate by URL and by title
    seen_urls = set()
    seen_titles = set()
    unique = []
    for p in all_posts:
        url_key = p["url"].rstrip("/").lower()
        title_key = p["title"].lower().strip()[:60]

        if url_key in seen_urls or title_key in seen_titles:
            continue

        seen_urls.add(url_key)
        seen_titles.add(title_key)
        unique.append(p)

    return unique[:limit]
