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

# Healthcare IT — clinics, hospitals, health-tech companies with EHR/EMR/integration pain
QUERIES = [
    # Epic
    'site:userweb.epic.com "error" OR "issue" OR "integration" OR "not working"',
    '"Epic EHR" OR "Epic Systems" "broken" OR "issue" OR "integration" OR "API" OR "HL7" site:reddit.com OR site:community.healthit.gov',
    # Cerner / Oracle Health
    '"Cerner" OR "Oracle Health" "not working" OR "broken" OR "error" OR "integration"',
    # General health IT
    'site:community.healthit.gov "issue" OR "error" OR "not working" OR "help"',
    'site:reddit.com/r/healthIT "broken" OR "error" OR "integration" OR "help" OR "need"',
    # Practice management / telehealth
    '"practice management" OR "EHR" OR "EMR" "not working" OR "broken" OR "need help" integration OR migration OR API',
    # HIPAA compliance tools
    '"HIPAA" "compliance" "tool" OR "software" "broken" OR "issue" OR "need" OR "help"',
]


class HealthcareITScraper(BaseScraper):
    """Healthcare IT forums — Epic, Cerner, EHR/EMR users needing integrations and fixes."""

    name = "Healthcare IT"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'"EHR" OR "healthcare IT" "{query}"',
                f'site:reddit.com/r/healthIT "{query}"',
                f'"medical software" "{query}"',
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

                    source = "Healthcare IT"
                    if "epic.com" in href:
                        source = "Epic"
                    elif "cerner" in href or "oracle" in href.lower():
                        source = "Cerner"
                    elif "healthit.gov" in href:
                        source = "HealthIT.gov"

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
