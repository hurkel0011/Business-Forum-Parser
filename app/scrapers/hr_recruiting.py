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

# HR / Recruiting / People ops platforms — HR teams needing automation and integrations
QUERIES = [
    # BambooHR
    'site:community.bamboohr.com "issue" OR "not working" OR "integration" OR "help"',
    '"BambooHR" "not working" OR "broken" OR "integration" OR "API" OR "bug"',
    # Workday
    '"Workday" "error" OR "not working" OR "integration" OR "broken" OR "help" site:reddit.com OR site:community.workday.com',
    # ADP
    '"ADP" "payroll" OR "workforce" "not working" OR "error" OR "broken" OR "integration"',
    # Greenhouse / Lever / ATS
    '"Greenhouse" OR "Lever" OR "ATS" "integration" OR "broken" OR "not working" OR "API" OR "bug"',
    # General HR tech
    '"HR software" OR "HRIS" OR "payroll software" "not working" OR "broken" OR "need help" integration OR automation',
    # Gusto / Rippling
    '"Gusto" OR "Rippling" "not working" OR "error" OR "broken" OR "integration" OR "help"',
]


class HRRecruitingScraper(BaseScraper):
    """HR/Recruiting platform forums — BambooHR, Workday, ADP users with integration and automation needs."""

    name = "HR / Recruiting"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'"HR software" OR "HRIS" "{query}"',
                f'"BambooHR" OR "Workday" OR "ADP" "{query}"',
                f'"payroll" OR "recruiting" "{query}"',
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

                    source = "HR Tech"
                    if "bamboohr" in href:
                        source = "BambooHR"
                    elif "workday" in href:
                        source = "Workday"
                    elif "adp.com" in href:
                        source = "ADP"
                    elif "greenhouse" in href:
                        source = "Greenhouse"
                    elif "lever.co" in href:
                        source = "Lever"
                    elif "gusto.com" in href:
                        source = "Gusto"
                    elif "rippling.com" in href:
                        source = "Rippling"

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
