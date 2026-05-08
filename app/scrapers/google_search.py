import requests
from urllib.parse import unquote
from bs4 import BeautifulSoup
from .base import BaseScraper


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}


class DuckDuckGoScraper(BaseScraper):
    """DuckDuckGo HTML scraper — no blocking, no API key."""

    name = "Web Search"

    FORUM_SITES = [
        "reddit.com", "community.microsoft.com", "techcommunity.microsoft.com",
        "answers.microsoft.com", "community.zapier.com", "community.atlassian.com",
        "community.hubspot.com", "community.shopify.com", "discussions.apple.com",
        "support.google.com", "stackoverflow.com", "superuser.com",
        "serverfault.com", "community.make.com", "community.airtable.com",
        "forum.quickbooks.intuit.com", "community.cloudflare.com",
        "community.n8n.io", "community.retool.com", "community.monday.com",
        "productforums.google.com", "feedback.azure.com",
    ]

    # Very specific complaint-focused search queries
    COMPLAINT_QUERIES = [
        # Direct pain + business forums
        '"frustrated with" OR "doesn\'t work" OR "completely broken" site:reddit.com/r/smallbusiness OR site:reddit.com/r/SaaS',
        '"help needed" OR "losing money" OR "critical bug" site:reddit.com/r/sysadmin OR site:reddit.com/r/msp',
        '"integration broken" OR "API not working" OR "sync failed" site:community.zapier.com OR site:community.make.com',
        '"workflow broken" OR "automation failed" OR "can\'t connect" forum OR community',
        '"switching from" OR "looking for alternative to" OR "replacing" software tool',
        '"need developer" OR "hire someone" OR "willing to pay" fix OR build OR automate',
        '"production issue" OR "data loss" OR "migration failed" OR "export broken"',

        # Specific product complaints
        'salesforce "not working" OR "broken" OR "frustrated" -tutorial -howto',
        'hubspot OR zendesk OR jira "bug" OR "issue" OR "broken" community OR forum',
        'shopify "can\'t" OR "doesn\'t" OR "broken" OR "need help" -tutorial',
        'quickbooks OR xero "integration" OR "export" OR "sync" problem OR issue OR broken',

        # Automation / integration gaps
        '"no integration" OR "manual process" OR "copy paste" OR "spreadsheet" automate OR solution',
        '"zapier can\'t" OR "make.com can\'t" OR "automation doesn\'t" OR "need custom"',

        # Stack Overflow unanswered
        'site:stackoverflow.com "no answers" OR "unanswered" business OR enterprise OR integration',
    ]

    def _search_ddg(self, query, max_results=25):
        posts = []
        try:
            resp = requests.post(
                "https://html.duckduckgo.com/html/",
                data={"q": query, "b": ""},
                headers=HEADERS,
                timeout=30,
            )
            if resp.status_code != 200:
                return posts

            soup = BeautifulSoup(resp.text, "html.parser")

            for result in soup.select(".result"):
                title_el = result.select_one(".result__a")
                snippet_el = result.select_one(".result__snippet")
                url_el = result.select_one(".result__url")

                if not title_el:
                    continue

                href = title_el.get("href", "")
                if "uddg=" in href:
                    href = unquote(href.split("uddg=")[1].split("&")[0])
                if not href.startswith("http"):
                    if url_el:
                        raw = url_el.get_text(strip=True)
                        if not raw.startswith("http"):
                            raw = "https://" + raw
                        href = raw
                if not href.startswith("http"):
                    continue

                source_site = "Web Search"
                for site in self.FORUM_SITES:
                    if site in href:
                        short = site.replace("community.", "").split(".")[0]
                        source_site = f"Web/{short.capitalize()}"
                        break

                posts.append({
                    "source": source_site,
                    "title": title_el.get_text(strip=True),
                    "content": snippet_el.get_text(strip=True) if snippet_el else "",
                    "url": href,
                    "author": "unknown",
                })

                if len(posts) >= max_results:
                    break

        except Exception:
            pass
        return posts

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                query,
                f"{query} forum complaint",
                f"{query} broken OR frustrated OR help",
            ]
        else:
            queries = self.COMPLAINT_QUERIES

        all_posts = []
        per_query = max(8, limit // len(queries))

        for q in queries:
            results = self._search_ddg(q, max_results=per_query)
            all_posts.extend(results)

        # Deduplicate by URL
        seen = set()
        unique = []
        for p in all_posts:
            if p["url"] not in seen:
                seen.add(p["url"])
                unique.append(p)

        return unique[:limit]
