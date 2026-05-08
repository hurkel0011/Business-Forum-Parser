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

# Additional freelance platforms — Fiverr requests, PeoplePerHour, Guru
QUERIES = [
    # Fiverr buyer requests / gigs wanted
    'site:fiverr.com "fix" OR "repair" OR "debug" website OR software OR app',
    'site:fiverr.com "build" OR "automate" OR "integrate" OR "migrate" OR "scrape"',
    'site:fiverr.com "urgent" OR "ASAP" developer OR programmer OR coder',
    # PeoplePerHour
    'site:peopleperhour.com "fix" OR "build" OR "develop" OR "automate" website OR software',
    'site:peopleperhour.com "API" OR "integration" OR "migration" OR "database"',
    # Guru
    'site:guru.com/jobs "fix" OR "repair" OR "debug" OR "develop" software OR website',
    'site:guru.com/jobs "automation" OR "integration" OR "migration" OR "scraping"',
    # Bark (service marketplace)
    'site:bark.com "web developer" OR "software developer" OR "app developer"',
]


class MoreFreelanceScraper(BaseScraper):
    """Additional freelance platforms — Fiverr, PeoplePerHour, Guru, Bark."""

    name = "More Freelance"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:fiverr.com "{query}"',
                f'site:peopleperhour.com "{query}"',
                f'site:guru.com "{query}"',
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

                    source = "Freelance"
                    if "fiverr.com" in href:
                        source = "Fiverr"
                    elif "peopleperhour.com" in href:
                        source = "PeoplePerHour"
                    elif "guru.com" in href:
                        source = "Guru"
                    elif "bark.com" in href:
                        source = "Bark"

                    all_posts.append({
                        "source": source,
                        "title": title_el.get_text(strip=True),
                        "content": snippet_el.get_text(strip=True) if snippet_el else "",
                        "url": href,
                        "author": "client",
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
