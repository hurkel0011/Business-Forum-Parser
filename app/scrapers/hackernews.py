import requests
from .base import BaseScraper


class HackerNewsScraper(BaseScraper):
    name = "Hacker News"

    DEFAULT_QUERIES = [
        # Integration pain — highest value
        "integration broken API sync",
        "webhook failing error production",
        "Salesforce HubSpot integration broken",
        "Zapier automation broken alternative",
        # Migration / switching
        "migrating from switching alternative frustrated",
        # Real pain signals
        "broken workflow automation need help",
        "production down error critical urgent",
        # Seeking solutions
        "need developer build tool script",
        "willing to pay custom solution",
        "looking for freelancer automate",
    ]

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [query]
        else:
            keywords = config.get("keywords", [])
            queries = self.DEFAULT_QUERIES
            if keywords:
                queries = [" ".join(keywords[i:i+3]) for i in range(0, len(keywords), 3)]
                queries = queries[:5]

        all_posts = []
        per_query = max(10, limit // len(queries))

        for q in queries:
            # Search stories and Ask HN
            for tag_set in ["(story,ask_hn)", "comment"]:
                try:
                    resp = requests.get(
                        "https://hn.algolia.com/api/v1/search_by_date",
                        params={
                            "query": q,
                            "tags": tag_set,
                            "hitsPerPage": min(per_query, 50),
                        },
                        timeout=30,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    for hit in data.get("hits", []):
                        story_text = (
                            hit.get("story_text")
                            or hit.get("comment_text")
                            or ""
                        )
                        title = (
                            hit.get("title")
                            or hit.get("story_title")
                            or ""
                        )
                        object_id = hit.get("objectID", "")

                        if not title and not story_text:
                            continue

                        # Skip product launches, promos, opinion pieces (not complaints)
                        title_lower = title.lower()
                        skip_prefixes = [
                            "show hn:", "launch hn:", "tell hn:",
                            "ask hn: what are you working",
                            "ask hn: who is hiring",
                            "ask hn: who wants to be hired",
                            "ask hn: freelancer?",
                        ]
                        skip_patterns = [
                            " is dead", " sucks", " is overrated",
                            " myths ", "why i stopped", "why i left",
                            "we're hiring", "job listing",
                        ]
                        if any(title_lower.startswith(p) for p in skip_prefixes):
                            continue
                        if any(p in title_lower for p in skip_patterns):
                            continue

                        all_posts.append({
                            "source": "Hacker News",
                            "title": title or story_text[:80],
                            "content": story_text[:2000],
                            "url": (
                                hit.get("url")
                                or f"https://news.ycombinator.com/item?id={object_id}"
                            ),
                            "author": hit.get("author", "unknown"),
                        })
                except Exception:
                    continue

        # Deduplicate
        seen = set()
        unique = []
        for p in all_posts:
            key = p["title"][:50]
            if key not in seen:
                seen.add(key)
                unique.append(p)

        return unique[:limit]
