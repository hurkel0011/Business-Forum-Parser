import requests
from .base import BaseScraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}

# Dev.to has a free public API — no auth needed
API_BASE = "https://dev.to/api/articles"

SEARCH_TAGS = [
    "help", "discuss", "watercooler", "productivity",
]

SEARCH_QUERIES = [
    "frustrated with",
    "broken tool",
    "need alternative",
    "automation problem",
    "integration issue",
    "looking for solution",
    "migration nightmare",
    "bug fix help",
]


class DevToScraper(BaseScraper):
    """Dev.to articles & discussions — developers writing about pain points and seeking help."""

    name = "Dev.to"

    def scrape(self, config, query=None, limit=50):
        posts = []
        seen_urls = set()  # O(1) dedup instead of O(n²) list scan

        if query:
            searches = [query]
        else:
            searches = SEARCH_QUERIES

        # Search by query terms — use Dev.to search API
        for term in searches:
            if len(posts) >= limit:
                break
            try:
                resp = requests.get(
                    "https://dev.to/api/articles",
                    params={"per_page": 10, "tag": "discuss,help", "search": term},
                    headers=HEADERS,
                    timeout=15,
                )
                if resp.status_code != 200:
                    continue

                for article in resp.json():
                    url = article.get("url", "")
                    if url in seen_urls:
                        continue
                    title = article.get("title", "")
                    desc = article.get("description", "")
                    combined = f"{title} {desc}".lower()

                    # Filter for pain/help signals
                    if query:
                        if query.lower() not in combined:
                            continue
                    else:
                        pain_words = [
                            "help", "broken", "fix", "issue", "problem", "error",
                            "frustrated", "alternative", "migrate", "stuck",
                            "bug", "doesn't work", "looking for", "need",
                            "automation", "integration", "urgent",
                        ]
                        if not any(w in combined for w in pain_words):
                            continue

                    seen_urls.add(url)
                    posts.append({
                        "source": "Dev.to",
                        "title": title,
                        "content": desc[:2000],
                        "url": url,
                        "author": article.get("user", {}).get("username", "unknown"),
                    })

            except Exception:
                continue

        # Also search by tags that indicate problems
        for tag in SEARCH_TAGS:
            if len(posts) >= limit:
                break
            try:
                resp = requests.get(
                    API_BASE,
                    params={"per_page": 8, "tag": tag, "state": "fresh"},
                    headers=HEADERS,
                    timeout=15,
                )
                if resp.status_code != 200:
                    continue

                for article in resp.json():
                    url = article.get("url", "")
                    if url in seen_urls:
                        continue

                    seen_urls.add(url)
                    posts.append({
                        "source": "Dev.to",
                        "title": article.get("title", ""),
                        "content": (article.get("description") or "")[:2000],
                        "url": url,
                        "author": article.get("user", {}).get("username", "unknown"),
                    })

            except Exception:
                continue

        return posts[:limit]
