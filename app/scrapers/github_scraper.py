import requests
from .base import BaseScraper


class GitHubScraper(BaseScraper):
    name = "GitHub Issues"

    def scrape(self, config, query=None, limit=50):
        keywords = config.get("keywords", [])
        search_query = query or " OR ".join(keywords[:3])
        search_query += " is:issue is:open"

        headers = {"Accept": "application/vnd.github.v3+json"}
        token = config.get("github_token", "")
        if token:
            headers["Authorization"] = f"token {token}"

        try:
            resp = requests.get(
                "https://api.github.com/search/issues",
                params={
                    "q": search_query,
                    "sort": "created",
                    "order": "desc",
                    "per_page": min(limit, 100),
                },
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            posts = []
            for item in data.get("items", []):
                posts.append({
                    "source": "GitHub Issues",
                    "title": item.get("title", ""),
                    "content": (item.get("body") or "")[:2000],
                    "url": item.get("html_url", ""),
                    "author": item.get("user", {}).get("login", "unknown"),
                })
            return posts[:limit]
        except Exception:
            return []
