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

# Discourse-based communities for no-code/automation/SaaS platforms
# These are where people hit platform limits and need custom dev work
FORUMS = [
    ("community.zapier.com", "Zapier"),
    ("community.airtable.com", "Airtable"),
    ("community.make.com", "Make/Integromat"),
    ("community.n8n.io", "n8n"),
    ("community.notion.so", "Notion"),
    ("discourse.webflow.com", "Webflow"),
    ("forum.bubble.io", "Bubble"),
    ("meta.discourse.org", "Discourse"),
    ("community.retool.com", "Retool"),
    ("community.monday.com", "Monday.com"),
]

PAIN_TERMS = [
    '"need help" OR "doesn\'t work" OR "broken"',
    '"how to" OR "is it possible" OR "workaround"',
    '"limitation" OR "can\'t do" OR "not supported" OR "alternative"',
    '"API" OR "integration" OR "webhook" OR "automation"',
]


class DiscourseScraper(BaseScraper):
    """No-code/SaaS community forums (Zapier, Airtable, Make, Notion, etc.) — people hitting platform limits."""

    name = "SaaS Communities"

    def scrape(self, config, query=None, limit=50):
        all_posts = []

        if query:
            # Search all forums for the custom query
            sites = " OR ".join(f"site:{domain}" for domain, _ in FORUMS)
            queries = [f'({sites}) "{query}"']
        else:
            # Rotate through forums with pain-signal queries
            queries = []
            for domain, name in FORUMS[:6]:
                term = PAIN_TERMS[len(queries) % len(PAIN_TERMS)]
                queries.append(f"site:{domain} {term}")

        per_query = max(6, limit // max(len(queries), 1))

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

                    # Tag by platform
                    source = "SaaS Forum"
                    for domain, name in FORUMS:
                        if domain in href:
                            source = name
                            break

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
