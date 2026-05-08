import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .base import BaseScraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Bing is what Edge uses under the hood — same results
COMPLAINT_QUERIES = [
    '"frustrated with" OR "completely broken" OR "losing money" software forum',
    '"integration broken" OR "API not working" OR "sync failed" community',
    '"need developer" OR "willing to pay" OR "hire someone" fix automate',
    '"switching from" OR "looking for alternative" OR "replacing" tool software',
    '"workflow broken" OR "manual process" OR "automation failed" business',
    '"production down" OR "critical bug" OR "urgent fix" support forum',
    '"can\'t export" OR "data migration" OR "import broken" help',
    'salesforce OR hubspot OR zendesk "broken" OR "frustrated" OR "issue"',
    'shopify OR quickbooks OR jira "bug" OR "not working" OR "help"',
    '"no integration" OR "need custom" OR "spreadsheet" automate OR script',
]


class BingSearchScraper(BaseScraper):
    """Bing / Edge search — different index than DDG, catches different results."""

    name = "Bing/Edge"

    def _search_bing(self, query, count=20):
        posts = []
        try:
            url = f"https://www.bing.com/search?q={quote_plus(query)}&count={count}"
            resp = requests.get(url, headers=HEADERS, timeout=25)
            if resp.status_code != 200:
                return posts

            soup = BeautifulSoup(resp.text, "html.parser")

            for result in soup.select("#b_results .b_algo"):
                title_el = result.select_one("h2 a")
                snippet_el = result.select_one(".b_caption p, .b_lineclamp2")

                if not title_el:
                    continue

                href = title_el.get("href", "")
                if not href.startswith("http"):
                    continue

                posts.append({
                    "source": "Bing/Edge",
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
                f"{query} site:reddit.com OR site:stackoverflow.com",
                f"{query} forum complaint help",
            ]
        else:
            queries = COMPLAINT_QUERIES

        all_posts = []
        per_query = max(8, limit // len(queries))

        for q in queries:
            results = self._search_bing(q, count=per_query)
            all_posts.extend(results)

        seen = set()
        unique = []
        for p in all_posts:
            if p["url"] not in seen:
                seen.add(p["url"])
                unique.append(p)

        return unique[:limit]
