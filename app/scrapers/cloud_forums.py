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
}

# Cloud/hosting communities — devops, sysadmins, developers with infrastructure problems
QUERIES = [
    # DigitalOcean
    'site:digitalocean.com/community "help" OR "error" OR "not working" OR "broken"',
    'site:digitalocean.com/community "migration" OR "deploy" OR "SSL" OR "DNS" issue',
    # Cloudflare
    'site:community.cloudflare.com "issue" OR "error" OR "not working" OR "blocked"',
    'site:community.cloudflare.com "help" OR "need" OR "how to" OR "workaround"',
    # AWS re:Post
    'site:repost.aws "error" OR "issue" OR "help" OR "not working"',
    'site:repost.aws "migration" OR "lambda" OR "S3" OR "EC2" problem OR fix',
    # Netlify
    'site:answers.netlify.com "deploy" OR "build" OR "error" OR "broken" OR "help"',
    # Vercel
    'site:github.com/vercel/next.js/discussions "bug" OR "help" OR "error" OR "issue"',
]


class CloudForumsScraper(BaseScraper):
    """Cloud/hosting community forums — DigitalOcean, Cloudflare, AWS, Netlify, Vercel."""

    name = "Cloud Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:digitalocean.com/community "{query}"',
                f'site:community.cloudflare.com "{query}"',
                f'site:repost.aws "{query}"',
            ]
        else:
            queries = QUERIES

        all_posts = []
        per_query = max(5, limit // len(queries))

        for q in queries:
            try:
                url = f"https://www.bing.com/search?q={quote_plus(q)}&count={per_query}"
                resp = requests.get(url, headers=HEADERS, timeout=20)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                for result in soup.select("#b_results .b_algo"):
                    title_el = result.select_one("h2 a")
                    snippet_el = result.select_one(".b_caption p")

                    if not title_el:
                        continue

                    href = title_el.get("href", "")
                    if not href.startswith("http"):
                        continue

                    source = "Cloud"
                    if "digitalocean.com" in href:
                        source = "DigitalOcean"
                    elif "cloudflare.com" in href:
                        source = "Cloudflare"
                    elif "repost.aws" in href or "aws.amazon" in href:
                        source = "AWS"
                    elif "netlify.com" in href:
                        source = "Netlify"
                    elif "vercel" in href or "next.js" in href:
                        source = "Vercel"

                    all_posts.append({
                        "source": source,
                        "title": title_el.get_text(strip=True),
                        "content": snippet_el.get_text(strip=True) if snippet_el else "",
                        "url": href,
                        "author": "unknown",
                    })

                time.sleep(0.5)
            except Exception:
                continue

        seen = set()
        unique = []
        for p in all_posts:
            if p["url"] not in seen:
                seen.add(p["url"])
                unique.append(p)

        return unique[:limit]
