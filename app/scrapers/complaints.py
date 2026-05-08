import requests
import time
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .base import BaseScraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
    ),
}

# Dedicated consumer complaint sites — people actively raging about broken services
QUERIES = [
    # BBB
    'site:bbb.org/complaint "software" OR "website" OR "app" OR "service"',
    'site:bbb.org/us "customer reviews" software OR technology OR web',
    # Sitejabber
    'site:sitejabber.com/reviews "terrible" OR "broken" OR "scam" OR "doesn\'t work" software',
    'site:sitejabber.com/reviews "website builder" OR "hosting" OR "saas" OR "crm"',
    # PissedConsumer
    'site:pissedconsumer.com "software" OR "app" OR "website" OR "service" broken OR terrible',
    'site:pissedconsumer.com "developer" OR "tech support" OR "integration" OR "data loss"',
    # ConsumerAffairs
    'site:consumeraffairs.com/technology "review" "1 star" OR "terrible" OR "avoid"',
    'site:consumeraffairs.com/computers "problem" OR "issue" OR "broken" OR "refund"',
]


class ComplaintsScraper(BaseScraper):
    """Consumer complaint sites — BBB, Sitejabber, PissedConsumer, ConsumerAffairs."""

    name = "Complaint Sites"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:bbb.org "{query}"',
                f'site:sitejabber.com "{query}"',
                f'site:pissedconsumer.com "{query}"',
                f'site:consumeraffairs.com "{query}"',
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

                    source = "Complaints"
                    if "bbb.org" in href:
                        source = "BBB"
                    elif "sitejabber.com" in href:
                        source = "Sitejabber"
                    elif "pissedconsumer.com" in href:
                        source = "PissedConsumer"
                    elif "consumeraffairs.com" in href:
                        source = "ConsumerAffairs"

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
