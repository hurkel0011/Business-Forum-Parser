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

# PropTech / Real estate tech — agents, property managers, real estate companies
QUERIES = [
    # Property management software
    '"AppFolio" OR "Buildium" OR "Rent Manager" "not working" OR "broken" OR "error" OR "integration"',
    '"property management software" "not working" OR "broken" OR "need help" OR "error" integration OR automation',
    # Real estate CRM
    '"Follow Up Boss" OR "kvCORE" OR "BoomTown" "not working" OR "broken" OR "integration" OR "error"',
    '"real estate CRM" "broken" OR "not working" OR "issue" OR "need help" integration OR API',
    # MLS / IDX
    '"MLS" OR "IDX" "integration" OR "not working" OR "broken" OR "error" OR "feed"',
    # Zillow / Realtor tech
    '"Zillow" OR "Realtor.com" "API" OR "integration" OR "not working" OR "broken" OR "sync"',
    # General proptech
    '"proptech" OR "real estate technology" "issue" OR "broken" OR "not working" OR "need" site:reddit.com',
]


class RealEstateTechScraper(BaseScraper):
    """PropTech/Real estate tech — property management, real estate CRM, MLS integration issues."""

    name = "Real Estate Tech"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'"property management" OR "real estate" "{query}"',
                f'"MLS" OR "IDX" "{query}"',
                f'"proptech" "{query}"',
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

                    source = "PropTech"
                    if "appfolio" in href:
                        source = "AppFolio"
                    elif "buildium" in href:
                        source = "Buildium"
                    elif "followupboss" in href:
                        source = "Follow Up Boss"
                    elif "kvcore" in href:
                        source = "kvCORE"
                    elif "zillow" in href:
                        source = "Zillow"

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
