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

# EdTech / LMS communities — schools and course creators with broken platforms
QUERIES = [
    # Canvas LMS
    'site:community.canvaslms.com "not working" OR "error" OR "broken" OR "help"',
    'site:community.canvaslms.com "integration" OR "API" OR "LTI" OR "sync"',
    # Moodle
    'site:moodle.org/mod/forum "error" OR "issue" OR "broken" OR "help" OR "plugin"',
    # Blackboard / Anthology
    'site:community.anthology.com "issue" OR "error" OR "not working" OR "help"',
    # Google Classroom / EdTech
    'site:support.google.com/edu "not working" OR "issue" OR "error" OR "broken"',
    # Teachable / Thinkific / Course platforms
    '"Teachable" OR "Thinkific" OR "Kajabi" "not working" OR "broken" OR "integration" OR "bug" site:community.teachable.com OR site:reddit.com',
    # General LMS complaints
    '"LMS" OR "learning management" "broken" OR "not working" OR "need help" integration OR API site:reddit.com',
]


class EducationScraper(BaseScraper):
    """EdTech/LMS forums — Canvas, Moodle, Blackboard, course platform users with integration issues."""

    name = "Education / LMS"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:community.canvaslms.com "{query}"',
                f'site:moodle.org/mod/forum "{query}"',
                f'"LMS" OR "edtech" "{query}"',
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

                    source = "EdTech"
                    if "canvaslms.com" in href:
                        source = "Canvas LMS"
                    elif "moodle.org" in href:
                        source = "Moodle"
                    elif "anthology.com" in href or "blackboard" in href:
                        source = "Blackboard"
                    elif "teachable.com" in href:
                        source = "Teachable"
                    elif "thinkific" in href:
                        source = "Thinkific"

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
