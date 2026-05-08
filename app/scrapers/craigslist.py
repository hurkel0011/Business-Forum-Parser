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

# Major metro areas — computer gigs and web/software services
CITIES = ["newyork", "losangeles", "chicago", "houston", "sfbay", "seattle", "boston", "atlanta", "denver", "miami"]
SECTIONS = ["cpg", "web"]  # cpg = computer gigs, web = web/info design


class CraigslistScraper(BaseScraper):
    """Craigslist computer gigs — people posting freelance work requests."""

    name = "Craigslist Gigs"

    def scrape(self, config, query=None, limit=50):
        posts = []
        search_query = query or "fix OR build OR develop OR automate OR website"

        for city in CITIES[:5]:
            for section in SECTIONS:
                if len(posts) >= limit:
                    break
                try:
                    url = f"https://{city}.craigslist.org/search/{section}"
                    resp = requests.get(
                        url,
                        params={"query": search_query},
                        headers=HEADERS,
                        timeout=15,
                    )
                    if resp.status_code != 200:
                        continue

                    soup = BeautifulSoup(resp.text, "html.parser")

                    for item in soup.select(".cl-search-result, .result-row"):
                        title_el = item.select_one(".titlestring a, .result-title")
                        price_el = item.select_one(".priceinfo, .result-price")

                        if not title_el:
                            continue

                        href = title_el.get("href", "")
                        if href and not href.startswith("http"):
                            href = f"https://{city}.craigslist.org{href}"

                        price = price_el.get_text(strip=True) if price_el else ""
                        title_text = title_el.get_text(strip=True)
                        if price:
                            title_text = f"[{price}] {title_text}"

                        posts.append({
                            "source": f"Craigslist/{city}",
                            "title": title_text,
                            "content": "",  # Will be enriched later
                            "url": href,
                            "author": "poster",
                        })

                except Exception:
                    continue

        return posts[:limit]
