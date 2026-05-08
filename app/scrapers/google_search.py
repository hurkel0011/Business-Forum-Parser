import requests
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
    """Uses DuckDuckGo HTML (no blocking, no API key)."""

    name = "Web Search"

    FORUM_SITES = [
        "reddit.com",
        "community.microsoft.com",
        "techcommunity.microsoft.com",
        "answers.microsoft.com",
        "community.zapier.com",
        "community.atlassian.com",
        "community.hubspot.com",
        "community.shopify.com",
        "discussions.apple.com",
        "support.google.com",
        "stackoverflow.com",
        "superuser.com",
        "serverfault.com",
        "community.make.com",
        "community.airtable.com",
        "forum.quickbooks.intuit.com",
        "community.cloudflare.com",
        "community.n8n.io",
    ]

    def _search_ddg(self, query, max_results=30):
        """Scrape DuckDuckGo HTML lite for results."""
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
                if href.startswith("//duckduckgo.com/l/?uddg="):
                    from urllib.parse import unquote
                    href = unquote(href.split("uddg=")[1].split("&")[0])

                if not href.startswith("http"):
                    if url_el:
                        raw = url_el.get_text(strip=True)
                        if not raw.startswith("http"):
                            raw = "https://" + raw
                        href = raw

                source_site = "Web Search"
                for site in self.FORUM_SITES:
                    if site in href:
                        short = site.split(".")[0]
                        if short == "community":
                            short = site.split(".")[1]
                        source_site = f"Web > {short.capitalize()}"
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
        keywords = config.get("keywords", [])

        if query:
            queries = [query]
        else:
            queries = [
                '"frustrated with" OR "doesn\'t work" OR "broken" site:reddit.com',
                '"help needed" OR "critical bug" OR "losing money" forum',
                '"looking for alternative" OR "switching from" software complaint',
                '"integration broken" OR "API issue" OR "workflow broken"',
                '"urgent fix needed" OR "production down" OR "blocking issue"',
                'site:community.atlassian.com OR site:community.hubspot.com bug',
                'site:stackoverflow.com "no solution" OR "still broken" business',
            ]

        all_posts = []
        per_query = max(10, limit // len(queries))

        for q in queries:
            results = self._search_ddg(q, max_results=per_query)
            all_posts.extend(results)

        seen_urls = set()
        unique = []
        for p in all_posts:
            if p["url"] not in seen_urls:
                seen_urls.add(p["url"])
                unique.append(p)

        return unique[:limit]
