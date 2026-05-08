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


class IndieHackersScraper(BaseScraper):
    name = "IndieHackers"

    # Pages where founders post problems
    PATHS = [
        "/group/technology/posts",
        "/group/growth/posts",
        "/group/product-feedback/posts",
    ]

    def scrape(self, config, query=None, limit=50):
        posts = []

        for path in self.PATHS:
            if len(posts) >= limit:
                break
            try:
                url = f"https://www.indiehackers.com{path}"
                resp = requests.get(url, headers=HEADERS, timeout=20)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                for post_el in soup.select(".feed-item, article"):
                    title_el = post_el.select_one("h2 a, h3 a, .feed-item__title a")
                    body_el = post_el.select_one(
                        ".feed-item__body, .content, p"
                    )

                    if not title_el:
                        continue

                    href = title_el.get("href", "")
                    if href and not href.startswith("http"):
                        href = "https://www.indiehackers.com" + href

                    posts.append({
                        "source": "IndieHackers",
                        "title": title_el.get_text(strip=True),
                        "content": (
                            body_el.get_text(strip=True)[:2000] if body_el else ""
                        ),
                        "url": href,
                        "author": "unknown",
                    })

            except Exception:
                continue

        return posts[:limit]
