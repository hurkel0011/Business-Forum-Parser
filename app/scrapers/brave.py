import requests
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
}

COMPLAINT_QUERIES = [
    '"frustrated" OR "broken" OR "not working" software business forum',
    '"integration issue" OR "API broken" OR "sync problem" community help',
    '"willing to pay" OR "need developer" OR "looking for solution" software',
    '"switching from" OR "alternative to" OR "replacing" saas crm erp',
    '"production down" OR "losing customers" OR "urgent" support fix',
    '"manual process" OR "need automation" OR "tedious" workflow business',
    '"data migration" OR "export problem" OR "import failed" software help',
]


class BraveSearchScraper(BaseScraper):
    """Brave Search — independent index, catches results others miss."""

    name = "Brave Search"

    def _search_brave(self, query, count=20):
        posts = []
        try:
            url = f"https://search.brave.com/search?q={quote_plus(query)}"
            resp = requests.get(url, headers=HEADERS, timeout=25)
            if resp.status_code != 200:
                return posts

            soup = BeautifulSoup(resp.text, "html.parser")

            for result in soup.select(".snippet"):
                title_el = result.select_one(".snippet-title, a.result-header")
                snippet_el = result.select_one(
                    ".snippet-description, .snippet-content"
                )
                link_el = result.select_one("a[href^='http']")

                if not title_el:
                    continue

                href = ""
                if link_el:
                    href = link_el.get("href", "")
                elif title_el.name == "a":
                    href = title_el.get("href", "")

                if not href.startswith("http"):
                    continue

                posts.append({
                    "source": "Brave",
                    "title": title_el.get_text(strip=True),
                    "content": snippet_el.get_text(strip=True) if snippet_el else "",
                    "url": href,
                    "author": "unknown",
                })

                if len(posts) >= count:
                    break

        except Exception:
            pass
        return posts

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                query,
                f"{query} community complaint forum",
                f"{query} broken frustrated help",
            ]
        else:
            queries = COMPLAINT_QUERIES

        all_posts = []
        per_query = max(8, limit // len(queries))

        for q in queries:
            results = self._search_brave(q, count=per_query)
            all_posts.extend(results)

        seen = set()
        unique = []
        for p in all_posts:
            if p["url"] not in seen:
                seen.add(p["url"])
                unique.append(p)

        return unique[:limit]
