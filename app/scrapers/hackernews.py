import requests
from .base import BaseScraper


class HackerNewsScraper(BaseScraper):
    name = "Hacker News"

    def scrape(self, config, query=None, limit=50):
        keywords = config.get("keywords", [])
        search_query = query or " ".join(keywords[:3])

        try:
            resp = requests.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={
                    "query": search_query,
                    "tags": "(story,ask_hn)",
                    "hitsPerPage": min(limit, 100),
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            posts = []
            for hit in data.get("hits", []):
                story_text = hit.get("story_text") or hit.get("comment_text") or ""
                title = hit.get("title") or hit.get("story_title") or ""
                object_id = hit.get("objectID", "")
                posts.append({
                    "source": "Hacker News",
                    "title": title,
                    "content": story_text[:2000],
                    "url": hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}",
                    "author": hit.get("author", "unknown"),
                })
            return posts[:limit]
        except Exception:
            return []
