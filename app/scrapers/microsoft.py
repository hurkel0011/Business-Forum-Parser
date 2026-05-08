import requests
from bs4 import BeautifulSoup
from .base import BaseScraper


class MicrosoftCommunityScraper(BaseScraper):
    name = "Microsoft Community"

    def scrape(self, config, query=None, limit=50):
        keywords = config.get("keywords", [])
        search_query = query or " ".join(keywords[:3])

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        posts = []
        try:
            resp = requests.get(
                "https://techcommunity.microsoft.com/t5/forums/searchpage/tab/message",
                params={
                    "filter": "location",
                    "q": search_query,
                    "collapse_discussion": "true",
                },
                headers=headers,
                timeout=30,
            )

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")

                for item in soup.select(".lia-search-result-message")[:limit]:
                    title_el = item.select_one(".message-subject a")
                    body_el = item.select_one(".lia-message-body-content")
                    author_el = item.select_one(".lia-user-name-link")

                    if title_el:
                        href = title_el.get("href", "")
                        if href and not href.startswith("http"):
                            href = "https://techcommunity.microsoft.com" + href
                        posts.append({
                            "source": "Microsoft Community",
                            "title": title_el.get_text(strip=True),
                            "content": (body_el.get_text(strip=True)[:2000] if body_el else ""),
                            "url": href,
                            "author": (author_el.get_text(strip=True) if author_el else "unknown"),
                        })
        except Exception:
            pass

        return posts[:limit]
