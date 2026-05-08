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
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}

COMPLAINT_QUERIES = [
    '"frustrated" OR "broken" OR "doesn\'t work" site:reddit.com business software',
    '"help needed" OR "critical bug" OR "losing money" forum community',
    '"integration broken" OR "workflow broken" OR "sync failed" support',
    '"switching from" OR "need alternative" OR "replacing" saas tool',
    '"need developer" OR "willing to pay" OR "hire" automate fix',
    '"manual process" OR "spreadsheet" OR "copy paste" automation needed',
    'site:community.atlassian.com OR site:community.hubspot.com bug issue',
    'site:community.zapier.com OR site:community.make.com "doesn\'t work"',
]


class GoogleSearchScraper(BaseScraper):
    """Google search — may rate-limit, used as supplement to DDG and Bing."""

    name = "Google"

    def _search_google(self, query, num=15):
        posts = []
        try:
            url = f"https://www.google.com/search?q={quote_plus(query)}&num={num}&hl=en"
            resp = requests.get(url, headers=HEADERS, timeout=20)

            if resp.status_code == 429:
                return posts  # rate limited, skip gracefully
            if resp.status_code != 200:
                return posts

            soup = BeautifulSoup(resp.text, "html.parser")

            for result in soup.select("div.g"):
                title_el = result.select_one("h3")
                link_el = result.select_one("a[href^='http']")
                snippet_el = result.select_one(
                    "div.VwiC3b, span.aCOpRe, div[data-sncf], div[style*='line']"
                )

                if not title_el or not link_el:
                    continue

                href = link_el.get("href", "")
                if not href.startswith("http"):
                    continue

                posts.append({
                    "source": "Google",
                    "title": title_el.get_text(strip=True),
                    "content": snippet_el.get_text(strip=True) if snippet_el else "",
                    "url": href,
                    "author": "unknown",
                })

                if len(posts) >= num:
                    break

        except Exception:
            pass
        return posts

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                query,
                f"{query} forum OR community complaint",
                f"{query} broken OR frustrated OR help needed",
            ]
        else:
            queries = COMPLAINT_QUERIES

        all_posts = []
        per_query = max(6, limit // len(queries))

        for q in queries:
            results = self._search_google(q, num=per_query)
            all_posts.extend(results)
            # Small delay to avoid Google rate limiting
            time.sleep(1.5)

        seen = set()
        unique = []
        for p in all_posts:
            if p["url"] not in seen:
                seen.add(p["url"])
                unique.append(p)

        return unique[:limit]
