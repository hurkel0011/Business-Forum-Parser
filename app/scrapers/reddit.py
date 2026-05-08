import praw
from .base import BaseScraper


class RedditScraper(BaseScraper):
    name = "Reddit"

    def scrape(self, config, query=None, limit=50):
        client_id = config.get("reddit_client_id", "")
        client_secret = config.get("reddit_client_secret", "")

        if not client_id or not client_secret:
            return []

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=config.get("reddit_user_agent", "ForumParser/1.0"),
        )

        subreddits = config.get("reddit_subreddits", ["smallbusiness"])
        keywords = config.get("keywords", [])
        search_query = query or " OR ".join(keywords[:5])

        posts = []
        per_sub = max(1, limit // len(subreddits))

        for sub_name in subreddits:
            try:
                subreddit = reddit.subreddit(sub_name)
                for post in subreddit.search(search_query, limit=per_sub, sort="new"):
                    posts.append({
                        "source": f"Reddit r/{sub_name}",
                        "title": post.title,
                        "content": (post.selftext or "")[:2000],
                        "url": f"https://reddit.com{post.permalink}",
                        "author": str(post.author) if post.author else "deleted",
                    })
            except Exception:
                continue

        return posts[:limit]
