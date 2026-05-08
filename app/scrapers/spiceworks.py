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

# Spiceworks — IT admins and sysadmins posting enterprise problems
QUERIES = [
    'site:community.spiceworks.com "need help" OR "looking for" software OR tool OR solution',
    'site:community.spiceworks.com "migration" OR "upgrade" OR "replace" server OR software',
    'site:community.spiceworks.com "broken" OR "not working" OR "error" OR "crash" application',
    'site:community.spiceworks.com "automate" OR "script" OR "powershell" OR "deploy"',
    'site:community.spiceworks.com "integration" OR "sync" OR "connect" OR "API" systems',
    'site:community.spiceworks.com "recommend" OR "alternative to" OR "better than" software',
]


class SpiceworksScraper(BaseScraper):
    """Spiceworks IT Community — sysadmins and IT pros with enterprise tool problems."""

    name = "Spiceworks"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'site:community.spiceworks.com "{query}"']
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
                    if not href.startswith("http") or "spiceworks.com" not in href:
                        continue

                    all_posts.append({
                        "source": "Spiceworks",
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
