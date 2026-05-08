import requests
from bs4 import BeautifulSoup
from .base import BaseScraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}

# Upwork RSS feeds for job categories (public, no auth)
RSS_FEEDS = [
    ("Web Development", "https://www.upwork.com/ab/feed/jobs/rss?q=fix+bug+OR+integration+OR+automation+OR+migration&sort=recency&proposals=0-4"),
    ("Software Dev", "https://www.upwork.com/ab/feed/jobs/rss?q=broken+OR+urgent+OR+fix+OR+repair+software&sort=recency&proposals=0-4"),
    ("API/Integration", "https://www.upwork.com/ab/feed/jobs/rss?q=api+integration+OR+webhook+OR+sync+OR+connector&sort=recency&proposals=0-4"),
    ("Automation", "https://www.upwork.com/ab/feed/jobs/rss?q=automate+OR+automation+OR+script+OR+bot&sort=recency&proposals=0-4"),
    ("Data/Migration", "https://www.upwork.com/ab/feed/jobs/rss?q=data+migration+OR+csv+import+OR+database+OR+export&sort=recency&proposals=0-4"),
]


class UpworkScraper(BaseScraper):
    """Upwork job listings — people literally paying for dev work."""

    name = "Upwork Jobs"

    def scrape(self, config, query=None, limit=50):
        posts = []

        if query:
            feeds = [(
                "Custom",
                f"https://www.upwork.com/ab/feed/jobs/rss?q={requests.utils.quote(query)}&sort=recency"
            )]
        else:
            feeds = RSS_FEEDS

        for category, url in feeds:
            if len(posts) >= limit:
                break
            try:
                resp = requests.get(url, headers=HEADERS, timeout=20)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "xml")
                for item in soup.find_all("item"):
                    title = item.find("title")
                    desc = item.find("description")
                    link = item.find("link")

                    if not title:
                        continue

                    # Clean HTML from description
                    desc_text = ""
                    if desc:
                        desc_soup = BeautifulSoup(desc.get_text(), "html.parser")
                        desc_text = desc_soup.get_text(strip=True)

                    posts.append({
                        "source": f"Upwork/{category}",
                        "title": title.get_text(strip=True),
                        "content": desc_text[:2000],
                        "url": link.get_text(strip=True) if link else "",
                        "author": "client",
                    })

            except Exception:
                continue

        return posts[:limit]
