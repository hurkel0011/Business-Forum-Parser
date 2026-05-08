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

# Apple Support Communities + Apple Developer Forums
QUERIES = [
    'site:discussions.apple.com "data migration" OR "transfer" OR "lost files" OR "backup"',
    'site:discussions.apple.com "app doesn\'t work" OR "crash" OR "bug" OR "broken"',
    'site:discussions.apple.com "automation" OR "shortcut" OR "script" OR "Automator"',
    'site:discussions.apple.com "enterprise" OR "MDM" OR "deployment" OR "management"',
    'site:developer.apple.com/forums "API" OR "integration" OR "bug" OR "workaround"',
    'site:developer.apple.com/forums "help" OR "issue" OR "error" OR "crash" OR "rejected"',
]


class AppleScraper(BaseScraper):
    """Apple Support & Developer Forums — users with software, migration, and automation issues."""

    name = "Apple Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:discussions.apple.com "{query}"',
                f'site:developer.apple.com/forums "{query}"',
            ]
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
                    if not href.startswith("http"):
                        continue
                    if "apple.com" not in href:
                        continue

                    source = "Apple Developer" if "developer.apple" in href else "Apple Support"

                    all_posts.append({
                        "source": source,
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
