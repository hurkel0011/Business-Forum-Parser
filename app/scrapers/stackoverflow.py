import requests
from .base import BaseScraper


class StackOverflowScraper(BaseScraper):
    """Stack Exchange API — no auth needed, 300 requests/day."""

    name = "Stack Overflow"

    SITES = ["stackoverflow", "superuser", "serverfault"]

    TAGS = [
        "api", "integration", "automation", "deployment", "database",
        "authentication", "performance", "security", "migration",
    ]

    def scrape(self, config, query=None, limit=50):
        keywords = config.get("keywords", [])
        search_query = query or ";".join(keywords[:5])

        posts = []
        per_site = max(10, limit // len(self.SITES))

        for site in self.SITES:
            try:
                resp = requests.get(
                    "https://api.stackexchange.com/2.3/search/advanced",
                    params={
                        "order": "desc",
                        "sort": "creation",
                        "q": search_query,
                        "accepted": "False",
                        "answers": "0",
                        "site": site,
                        "pagesize": min(per_site, 100),
                        "filter": "withbody",
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()

                for item in data.get("items", []):
                    from html import unescape
                    body = unescape(item.get("body", ""))
                    from bs4 import BeautifulSoup
                    body_text = BeautifulSoup(body, "html.parser").get_text()

                    posts.append({
                        "source": f"StackExchange/{site}",
                        "title": unescape(item.get("title", "")),
                        "content": body_text[:2000],
                        "url": item.get("link", ""),
                        "author": item.get("owner", {}).get("display_name", "unknown"),
                    })
            except Exception:
                continue

        # Also get high-view unanswered questions (high business value)
        try:
            resp = requests.get(
                "https://api.stackexchange.com/2.3/questions/no-answers",
                params={
                    "order": "desc",
                    "sort": "votes",
                    "site": "stackoverflow",
                    "tagged": ";".join(self.TAGS[:5]),
                    "pagesize": 20,
                    "filter": "withbody",
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("items", []):
                if item.get("view_count", 0) > 100:
                    from html import unescape
                    body = unescape(item.get("body", ""))
                    from bs4 import BeautifulSoup
                    body_text = BeautifulSoup(body, "html.parser").get_text()

                    posts.append({
                        "source": "StackOverflow/high-demand",
                        "title": unescape(item.get("title", "")),
                        "content": body_text[:2000],
                        "url": item.get("link", ""),
                        "author": item.get("owner", {}).get("display_name", "unknown"),
                    })
        except Exception:
            pass

        return posts[:limit]
