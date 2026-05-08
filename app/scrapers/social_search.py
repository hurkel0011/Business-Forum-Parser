import requests
import time
from urllib.parse import unquote, quote_plus
from bs4 import BeautifulSoup
from .base import BaseScraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


class SocialMediaScraper(BaseScraper):
    """Search Facebook groups, Twitter/X, LinkedIn, and Reddit via Bing."""

    name = "Social Media"

    # Targeted searches across social platforms
    QUERIES = [
        # Facebook groups — business owners asking for help
        'site:facebook.com/groups "need developer" OR "looking for someone to build" OR "website help"',
        'site:facebook.com/groups "fix my website" OR "software issue" OR "need automation"',
        'site:facebook.com/groups "small business" "need help" software OR website OR app',

        # LinkedIn — professionals posting about problems
        'site:linkedin.com/posts "frustrated with" OR "broken" OR "need a developer"',
        'site:linkedin.com/posts "looking for" developer OR freelancer OR "someone to build"',
        'site:linkedin.com/pulse "software problem" OR "integration issue" OR "automation"',

        # Twitter/X — complaints and requests
        'site:twitter.com OR site:x.com "need developer" OR "hire developer" OR "looking for freelancer"',
        'site:twitter.com OR site:x.com "broken software" OR "integration doesn\'t work" OR "urgent fix"',

        # Reddit business subs via Bing (different results than DDG)
        'site:reddit.com/r/smallbusiness OR site:reddit.com/r/Entrepreneur "need help" software OR automation',
        'site:reddit.com/r/webdev OR site:reddit.com/r/freelance "client needs" OR "project" OR "looking for"',
        'site:reddit.com/r/forhire OR site:reddit.com/r/slavelabour "[hiring]" OR "looking for" developer OR automation',
    ]

    def _search_bing(self, query, count=15):
        posts = []
        try:
            url = f"https://www.bing.com/search?q={quote_plus(query)}&count={count}"
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                return posts

            soup = BeautifulSoup(resp.text, "html.parser")
            for result in soup.select("#b_results .b_algo"):
                title_el = result.select_one("h2 a")
                snippet_el = result.select_one(".b_caption p, .b_lineclamp2")

                if not title_el:
                    continue

                href = title_el.get("href", "")
                if not href.startswith("http"):
                    continue

                # Tag source by platform
                source = "Social"
                if "facebook.com" in href:
                    source = "Facebook"
                elif "linkedin.com" in href:
                    source = "LinkedIn"
                elif "twitter.com" in href or "x.com" in href:
                    source = "Twitter/X"
                elif "reddit.com" in href:
                    source = "Reddit"

                posts.append({
                    "source": source,
                    "title": title_el.get_text(strip=True),
                    "content": snippet_el.get_text(strip=True) if snippet_el else "",
                    "url": href,
                    "author": "unknown",
                })

                if len(posts) >= count:
                    break
        except Exception:
            pass
        return posts

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:facebook.com/groups "{query}"',
                f'site:linkedin.com/posts "{query}"',
                f'site:twitter.com OR site:x.com "{query}"',
                f'site:reddit.com "{query}" hire OR need OR help',
            ]
        else:
            queries = self.QUERIES

        all_posts = []
        per_query = max(6, limit // len(queries))

        for q in queries:
            results = self._search_bing(q, count=per_query)
            all_posts.extend(results)
            time.sleep(0.5)

        seen = set()
        unique = []
        for p in all_posts:
            if p["url"] not in seen:
                seen.add(p["url"])
                unique.append(p)

        return unique[:limit]
