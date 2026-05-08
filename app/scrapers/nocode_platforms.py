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

# No-code / Low-code platforms — business users hitting platform limitations
QUERIES = [
    # Airtable
    'site:community.airtable.com "not working" OR "error" OR "broken" OR "help" OR "limitation"',
    'site:community.airtable.com "automation" OR "integration" OR "API" OR "sync" issue',
    # Zapier
    'site:community.zapier.com "not working" OR "error" OR "broken" OR "help"',
    'site:community.zapier.com "integration" OR "trigger" OR "action" OR "zap" issue',
    # Make (Integromat)
    'site:community.make.com "error" OR "not working" OR "broken" OR "help"',
    # Bubble
    'site:forum.bubble.io "bug" OR "error" OR "not working" OR "broken" OR "help"',
    'site:forum.bubble.io "API" OR "plugin" OR "integration" issue',
    # Notion
    'site:reddit.com/r/Notion "not working" OR "broken" OR "API" OR "integration" OR "automation"',
    # Monday.com
    '"monday.com" "not working" OR "broken" OR "integration" OR "automation" OR "error" OR "API"',
    # General no-code
    '"no-code" OR "low-code" "limitation" OR "broken" OR "need developer" OR "custom" OR "workaround"',
]


class NoCodePlatformsScraper(BaseScraper):
    """No-code/Low-code platform forums — Airtable, Zapier, Make, Bubble users hitting limitations."""

    name = "No-Code / Low-Code"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:community.airtable.com "{query}"',
                f'site:community.zapier.com "{query}"',
                f'site:forum.bubble.io "{query}"',
                f'"no-code" OR "low-code" "{query}"',
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

                    source = "No-Code"
                    if "airtable.com" in href:
                        source = "Airtable"
                    elif "zapier.com" in href:
                        source = "Zapier"
                    elif "make.com" in href or "integromat" in href:
                        source = "Make"
                    elif "bubble.io" in href:
                        source = "Bubble"
                    elif "notion" in href.lower():
                        source = "Notion"
                    elif "monday.com" in href:
                        source = "Monday.com"

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
