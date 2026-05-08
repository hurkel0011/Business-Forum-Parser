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

# Legal tech — law firms and legal teams needing software fixes and automation
QUERIES = [
    # Clio
    'site:community.clio.com "issue" OR "not working" OR "error" OR "integration" OR "help"',
    '"Clio" "law" OR "legal" "not working" OR "broken" OR "integration" OR "bug"',
    # MyCase / PracticePanther
    '"MyCase" OR "PracticePanther" "not working" OR "broken" OR "error" OR "integration"',
    # Legal practice management
    '"legal software" OR "practice management" "not working" OR "broken" OR "need help" integration OR automation',
    # Contract / document automation
    '"contract management" OR "document automation" "broken" OR "not working" OR "error" OR "need" OR "help"',
    # Legal billing
    '"legal billing" OR "time tracking" "law firm" "not working" OR "broken" OR "error" OR "integration"',
    # General legal tech complaints
    '"legal tech" OR "lawtech" "issue" OR "problem" OR "not working" OR "integration" site:reddit.com OR site:lawtechnologytoday.org',
]


class LegalTechScraper(BaseScraper):
    """Legal tech forums — Clio, practice management tools, law firms with software issues."""

    name = "Legal Tech"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'"legal software" OR "law firm" "{query}"',
                f'site:community.clio.com "{query}"',
                f'"legal tech" "{query}"',
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

                    source = "Legal Tech"
                    if "clio.com" in href:
                        source = "Clio"
                    elif "mycase" in href:
                        source = "MyCase"
                    elif "practicepanther" in href:
                        source = "PracticePanther"

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
