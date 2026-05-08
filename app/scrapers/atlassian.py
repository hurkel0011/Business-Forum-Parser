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

# Atlassian Community — Jira, Confluence, Bitbucket, Trello problems
QUERIES = [
    'site:community.atlassian.com "Jira" "not working" OR "broken" OR "error" OR "bug"',
    'site:community.atlassian.com "Confluence" "help" OR "issue" OR "fix" OR "migrate"',
    'site:community.atlassian.com "integration" OR "API" OR "webhook" OR "automation"',
    'site:community.atlassian.com "workflow" OR "custom field" OR "plugin" OR "marketplace"',
    'site:community.atlassian.com "Bitbucket" OR "pipeline" error OR broken OR "doesn\'t work"',
    'site:community.atlassian.com "need help" OR "urgent" OR "anyone know how"',
]


class AtlassianScraper(BaseScraper):
    """Atlassian Community — Jira, Confluence, Bitbucket users with dev tool problems."""

    name = "Atlassian"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'site:community.atlassian.com "{query}"']
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
                    if not href.startswith("http") or "atlassian.com" not in href:
                        continue

                    all_posts.append({
                        "source": "Atlassian",
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
