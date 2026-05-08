"""
Shared search utility for all scrapers.
Uses Bing with domain-keyword targeting (not site: operator which triggers CAPTCHAs).

Author: Howell Brady | Origin: BonnieTheDog420
"""

import requests
import time
import random
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) "
        "Gecko/20100101 Firefox/128.0"
    ),
]


def _get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }


def bing_search(query, count=10):
    """Search Bing and return list of (title, snippet, url) tuples.

    IMPORTANT: Do NOT use 'site:' operator in queries — Bing blocks it with CAPTCHAs.
    Instead use the domain as a keyword: 'community.cloudflare.com error not working'
    """
    results = []
    try:
        url = f"https://www.bing.com/search?q={quote_plus(query)}&count={count}"
        resp = requests.get(url, headers=_get_headers(), timeout=20)
        if resp.status_code != 200:
            return results

        soup = BeautifulSoup(resp.text, "html.parser")

        for item in soup.select("#b_results .b_algo"):
            title_el = item.select_one("h2 a")
            snippet_el = item.select_one(".b_caption p, .b_lineclamp2")

            if not title_el:
                continue

            href = title_el.get("href", "")
            if not href.startswith("http"):
                continue

            results.append({
                "title": title_el.get_text(strip=True),
                "content": snippet_el.get_text(strip=True) if snippet_el else "",
                "url": href,
            })

            if len(results) >= count:
                break

    except Exception:
        pass

    return results


def search_domain(domain, terms, source_name="Web", count=10, url_filter=None):
    """Search for posts on a specific domain using Bing keyword targeting.

    Args:
        domain: Domain keyword to target (e.g. 'community.cloudflare.com')
        terms: Search terms (e.g. '"error" OR "not working" OR "help"')
        source_name: Default source label for results
        count: Max results to return
        url_filter: Optional function(url) -> source_name or None to filter/label results

    Returns:
        List of post dicts with title, content, url, author, source keys
    """
    query = f"{domain} {terms}"
    raw = bing_search(query, count=count)

    posts = []
    for item in raw:
        href = item["url"]

        # Apply URL filter if provided
        if url_filter:
            label = url_filter(href)
            if label is None:
                continue  # Skip URLs that don't match
            source = label
        else:
            source = source_name

        posts.append({
            "source": source,
            "title": item["title"],
            "content": item["content"],
            "url": href,
            "author": "unknown",
        })

    return posts


def multi_domain_search(queries, source_name="Web", limit=50, url_filter=None, delay=0.3):
    """Run multiple search queries and deduplicate results.

    Args:
        queries: List of search query strings (NO site: operator!)
        source_name: Default source label
        limit: Max total results
        url_filter: Optional function(url) -> source_name or None
        delay: Seconds between queries to avoid rate limiting

    Returns:
        Deduplicated list of post dicts
    """
    all_posts = []
    per_query = max(5, limit // len(queries))

    for q in queries:
        raw = bing_search(q, count=per_query)

        for item in raw:
            href = item["url"]

            if url_filter:
                label = url_filter(href)
                if label is None:
                    continue
                source = label
            else:
                source = source_name

            all_posts.append({
                "source": source,
                "title": item["title"],
                "content": item["content"],
                "url": href,
                "author": "unknown",
            })

        if delay > 0:
            time.sleep(delay + random.uniform(0, 0.2))

    # Deduplicate by URL
    seen = set()
    unique = []
    for p in all_posts:
        if p["url"] not in seen:
            seen.add(p["url"])
            unique.append(p)

    return unique[:limit]
