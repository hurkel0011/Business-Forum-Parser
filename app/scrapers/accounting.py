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

# Accounting/finance software communities — businesses needing integrations and fixes
QUERIES = [
    # QuickBooks
    'site:quickbooks.intuit.com/learn-support "not working" OR "error" OR "broken" OR "help"',
    'site:quickbooks.intuit.com/learn-support "integration" OR "import" OR "export" OR "sync"',
    # Xero
    'site:central.xero.com "issue" OR "error" OR "broken" OR "help" OR "integration"',
    # FreshBooks
    'site:support.freshbooks.com "issue" OR "not working" OR "help" OR "integration"',
    # Wave
    'site:support.waveapps.com "issue" OR "not working" OR "help" OR "integration"',
    # Sage
    'site:communityhub.sage.com "error" OR "issue" OR "help" OR "not working"',
    # General accounting software complaints
    '"accounting software" "not working" OR "broken" OR "need help" integration OR migration site:reddit.com OR site:quora.com',
]


class AccountingScraper(BaseScraper):
    """Accounting/finance software forums — QuickBooks, Xero, Sage users with integration issues."""

    name = "Accounting Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:quickbooks.intuit.com "{query}"',
                f'site:central.xero.com "{query}"',
                f'site:communityhub.sage.com "{query}"',
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

                    source = "Accounting"
                    if "quickbooks" in href or "intuit.com" in href:
                        source = "QuickBooks"
                    elif "xero.com" in href:
                        source = "Xero"
                    elif "freshbooks.com" in href:
                        source = "FreshBooks"
                    elif "waveapps.com" in href:
                        source = "Wave"
                    elif "sage.com" in href:
                        source = "Sage"

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
