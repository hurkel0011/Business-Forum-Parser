import requests
import time
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .base import BaseScraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}

# Shopify Community — merchants posting about store problems
QUERIES = [
    'site:community.shopify.com "need help" OR "broken" OR "not working" theme OR app',
    'site:community.shopify.com "custom code" OR "hire developer" OR "need someone to"',
    'site:community.shopify.com "checkout" OR "payment" OR "shipping" issue OR error OR broken',
    'site:community.shopify.com "migrate" OR "moving from" OR "switch to shopify"',
    'site:community.shopify.com "speed" OR "slow" OR "SEO" OR "conversion" fix OR help',
    'site:community.shopify.com "integration" OR "API" OR "app doesn\'t" OR "sync" problem',
]


class ShopifyScraper(BaseScraper):
    """Shopify Community forums — merchants needing dev help with their stores."""

    name = "Shopify Community"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'site:community.shopify.com "{query}"']
        else:
            queries = QUERIES

        all_posts = []
        per_query = max(6, limit // len(queries))

        for q in queries:
            try:
                url = f"https://www.bing.com/search?q={quote_plus(q)}&count={per_query}"
                resp = requests.get(url, headers=HEADERS, timeout=20)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                for result in soup.select("#b_results .b_algo"):
                    title_el = result.select_one("h2 a")
                    snippet_el = result.select_one(".b_caption p")

                    if not title_el:
                        continue

                    href = title_el.get("href", "")
                    if not href.startswith("http") or "community.shopify.com" not in href:
                        continue

                    all_posts.append({
                        "source": "Shopify",
                        "title": title_el.get_text(strip=True),
                        "content": snippet_el.get_text(strip=True) if snippet_el else "",
                        "url": href,
                        "author": "unknown",
                    })

                time.sleep(0.5)
            except Exception:
                continue

        seen = set()
        unique = []
        for p in all_posts:
            if p["url"] not in seen:
                seen.add(p["url"])
                unique.append(p)

        return unique[:limit]
