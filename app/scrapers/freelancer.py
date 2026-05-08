import requests
import time
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .base import BaseScraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
    ),
}

# Freelancer.com project listings found via Bing
QUERIES = [
    'site:freelancer.com/projects "fix" OR "repair" OR "debug" website OR software OR app',
    'site:freelancer.com/projects "build" OR "develop" OR "create" automation OR integration OR tool',
    'site:freelancer.com/projects "migrate" OR "convert" OR "transfer" data OR website OR database',
    'site:freelancer.com/projects "API" OR "integration" OR "webhook" OR "sync" OR "connector"',
    'site:freelancer.com/projects "urgent" OR "ASAP" OR "immediately" developer OR programmer',
    'site:freelancer.com/projects "scraping" OR "automation" OR "bot" OR "script"',
]


class FreelancerScraper(BaseScraper):
    """Freelancer.com project listings — clients posting jobs with budgets."""

    name = "Freelancer.com"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'site:freelancer.com/projects "{query}"']
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
                    if not href.startswith("http") or "freelancer.com" not in href:
                        continue

                    all_posts.append({
                        "source": "Freelancer.com",
                        "title": title_el.get_text(strip=True),
                        "content": snippet_el.get_text(strip=True) if snippet_el else "",
                        "url": href,
                        "author": "client",
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
