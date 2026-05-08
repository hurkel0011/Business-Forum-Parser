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

# SEO, marketing, and growth forums — business owners looking for tech help
QUERIES = [
    # Warrior Forum
    'site:warriorforum.com "need help" OR "looking for" developer OR programmer OR coder',
    'site:warriorforum.com "fix" OR "build" OR "automate" website OR software OR tool',
    # GrowthHackers
    'site:growthhackers.com "problem" OR "issue" OR "help" OR "looking for" tool OR software',
    # Moz Community (SEO)
    'site:moz.com/community "help" OR "issue" OR "broken" OR "fix" SEO OR website',
    # SitePoint
    'site:sitepoint.com/community "help" OR "error" OR "not working" OR "how to fix"',
    # WebmasterWorld
    'site:webmasterworld.com "issue" OR "problem" OR "broken" OR "need help" website',
    # Digital Point
    'site:forums.digitalpoint.com "need developer" OR "hire" OR "fix" OR "build"',
    # eCommerceFuel (private but indexed)
    'site:ecommercefuel.com "problem" OR "issue" OR "help" OR "looking for" developer',
]


class MarketingForumsScraper(BaseScraper):
    """SEO/marketing/webmaster forums — Warrior Forum, Moz, SitePoint, GrowthHackers."""

    name = "Marketing Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:warriorforum.com "{query}"',
                f'site:growthhackers.com "{query}"',
                f'site:moz.com/community "{query}"',
                f'site:sitepoint.com/community "{query}"',
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

                    source = "Marketing"
                    if "warriorforum.com" in href:
                        source = "WarriorForum"
                    elif "growthhackers.com" in href:
                        source = "GrowthHackers"
                    elif "moz.com" in href:
                        source = "Moz"
                    elif "sitepoint.com" in href:
                        source = "SitePoint"
                    elif "webmasterworld.com" in href:
                        source = "WebmasterWorld"
                    elif "digitalpoint.com" in href:
                        source = "DigitalPoint"

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
