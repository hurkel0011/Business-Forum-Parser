import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from .base import BaseScraper


class GoogleSearchScraper(BaseScraper):
    name = "Google Search"

    SITE_TARGETS = [
        "site:reddit.com",
        "site:community.microsoft.com OR site:techcommunity.microsoft.com",
        "site:community.zapier.com",
        "site:community.atlassian.com",
        "site:answers.microsoft.com",
        "site:community.hubspot.com",
        "site:community.shopify.com",
        "site:support.google.com",
        "site:discussions.apple.com",
    ]

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    def scrape(self, config, query=None, limit=50):
        keywords = config.get("keywords", [])
        base_query = query or " OR ".join(f'"{k}"' for k in keywords[:4])

        sites_query = " OR ".join(self.SITE_TARGETS[:5])
        full_query = f"({base_query}) ({sites_query})"

        posts = []
        try:
            url = f"https://www.google.com/search?q={quote_plus(full_query)}&num={min(limit, 100)}"
            resp = requests.get(url, headers=self.HEADERS, timeout=30)

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")

                for result in soup.select("div.g, div[data-sokoban-container]"):
                    title_el = result.select_one("h3")
                    link_el = result.select_one("a[href]")
                    snippet_el = result.select_one(
                        "div.VwiC3b, span.aCOpRe, div[data-sncf]"
                    )

                    if title_el and link_el:
                        href = link_el.get("href", "")
                        if not href.startswith("http"):
                            continue

                        source_site = "Google Search"
                        if "reddit.com" in href:
                            source_site = "Google > Reddit"
                        elif "microsoft.com" in href:
                            source_site = "Google > Microsoft"
                        elif "zapier.com" in href:
                            source_site = "Google > Zapier"
                        elif "atlassian.com" in href:
                            source_site = "Google > Atlassian"
                        elif "apple.com" in href:
                            source_site = "Google > Apple"
                        elif "hubspot.com" in href:
                            source_site = "Google > HubSpot"
                        elif "shopify.com" in href:
                            source_site = "Google > Shopify"

                        posts.append({
                            "source": source_site,
                            "title": title_el.get_text(strip=True),
                            "content": (
                                snippet_el.get_text(strip=True) if snippet_el else ""
                            ),
                            "url": href,
                            "author": "unknown",
                        })
        except Exception:
            pass

        return posts[:limit]
