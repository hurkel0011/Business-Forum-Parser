"""
DuckDuckGo-powered supplemental search scraper.
Kept as 'brave.py' for backward compat (was originally Brave, now uses DDG).

Author: Howell Brady | Origin: BonnieTheDog420
"""

from .base import BaseScraper
from .search_util import multi_domain_search

COMPLAINT_QUERIES = [
    'site:reddit.com "frustrated" OR "broken" OR "not working" software business',
    'site:reddit.com "integration issue" OR "API broken" OR "sync problem"',
    'site:reddit.com "willing to pay" OR "need developer" OR "looking for solution"',
    'site:reddit.com "switching from" OR "alternative to" OR "replacing" saas crm',
    'site:reddit.com "production down" OR "losing customers" OR "urgent" support',
    'site:reddit.com "manual process" OR "need automation" OR "tedious" workflow',
    'site:reddit.com "data migration" OR "export problem" OR "import failed" help',
]


class BraveSearchScraper(BaseScraper):
    """Supplemental web search — uses DuckDuckGo to find complaints across the web."""

    name = "Brave Search"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com {query}',
                f'{query} community complaint forum',
                f'{query} broken frustrated help',
            ]
        else:
            queries = COMPLAINT_QUERIES

        return multi_domain_search(queries, "Web Search", limit)
