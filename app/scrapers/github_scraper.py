import logging

import requests
from .base import BaseScraper

log = logging.getLogger(__name__)


class GitHubScraper(BaseScraper):
    name = "GitHub Issues"

    DEFAULT_QUERIES = [
        # High-value: labeled for outside help
        "label:\"help wanted\" integration",
        "label:\"help wanted\" migration",
        "label:\"help wanted\" automation",
        # Integration pain
        "integration broken API error",
        "webhook failing sync broken",
        "connector broken data loss",
        # Migration / breaking changes
        "breaking change migration blocked",
        "upgrade broke production regression",
        # Real pain with engagement
        "production issue critical urgent workaround",
    ]

    def scrape(self, config, query=None, limit=50):
        headers = {"Accept": "application/vnd.github.v3+json"}
        token = config.get("github_token", "")
        if token:
            headers["Authorization"] = f"token {token}"

        if query:
            queries = [f"{query} is:issue is:open"]
        else:
            queries = [f"{q} is:issue is:open" for q in self.DEFAULT_QUERIES]

        all_posts = []
        per_query = max(10, limit // len(queries))

        for search_query in queries:
            try:
                resp = requests.get(
                    "https://api.github.com/search/issues",
                    params={
                        "q": search_query,
                        "sort": "created",
                        "order": "desc",
                        "per_page": min(per_query, 30),
                    },
                    headers=headers,
                    timeout=30,
                )
                if resp.status_code == 403:
                    break  # rate limited
                resp.raise_for_status()
                data = resp.json()

                for item in data.get("items", []):
                    body = (item.get("body") or "")[:2000]
                    repo_url = item.get("repository_url", "")
                    repo_name = "/".join(repo_url.split("/")[-2:]) if repo_url else ""

                    all_posts.append({
                        "source": f"GitHub/{repo_name}" if repo_name else "GitHub Issues",
                        "title": item.get("title", ""),
                        "content": body,
                        "url": item.get("html_url", ""),
                        "author": item.get("user", {}).get("login", "unknown"),
                    })
            except Exception as e:
                log.debug("github query failed: %s: %s", search_query[:60], e)
                continue

        # Deduplicate by URL
        seen = set()
        unique = []
        for p in all_posts:
            if p["url"] not in seen:
                seen.add(p["url"])
                unique.append(p)

        return unique[:limit]
