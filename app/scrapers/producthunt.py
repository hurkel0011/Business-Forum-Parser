import requests
from bs4 import BeautifulSoup
from .base import BaseScraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}


class ProductHuntScraper(BaseScraper):
    """Product Hunt discussions — complaints about existing tools, feature requests."""

    name = "Product Hunt"

    CATEGORIES = [
        "developer-tools",
        "saas",
        "productivity",
        "marketing",
        "design-tools",
    ]

    def scrape(self, config, query=None, limit=50):
        posts = []

        # Search Product Hunt discussions via Bing
        from urllib.parse import quote_plus

        if query:
            queries = [f'site:producthunt.com "{query}"']
        else:
            queries = [
                'site:producthunt.com "alternative to" OR "better than" OR "replacement for"',
                'site:producthunt.com "frustrated" OR "broken" OR "doesn\'t work"',
                'site:producthunt.com "need a tool" OR "looking for" OR "anyone built"',
            ]

        for q in queries:
            try:
                url = f"https://www.bing.com/search?q={quote_plus(q)}&count=20"
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
                    if not href.startswith("http") or "producthunt.com" not in href:
                        continue

                    posts.append({
                        "source": "ProductHunt",
                        "title": title_el.get_text(strip=True),
                        "content": snippet_el.get_text(strip=True) if snippet_el else "",
                        "url": href,
                        "author": "unknown",
                    })
            except Exception:
                continue

        return posts[:limit]
