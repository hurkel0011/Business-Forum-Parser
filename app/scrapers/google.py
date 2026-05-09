"""
DuckDuckGo-powered supplemental search scraper.
Kept as 'google.py' for backward compat (was originally Google, now uses DDG).

Author: Howell Brady | Origin: BonnieTheDog420
"""

from .base import BaseScraper
from .search_util import multi_domain_search

COMPLAINT_QUERIES = [
    'site:reddit.com "frustrated" OR "broken" OR "doesn\'t work" business software',
    'site:reddit.com "help needed" OR "critical bug" OR "losing money" software',
    'site:reddit.com "integration broken" OR "workflow broken" OR "sync failed"',
    'site:reddit.com "switching from" OR "need alternative" saas tool',
    'site:reddit.com "need developer" OR "willing to pay" OR "hire" automate fix',
    'site:reddit.com "manual process" OR "spreadsheet" OR "copy paste" automation',
    'site:community.atlassian.com OR site:community.hubspot.com bug issue',
    'site:community.zapier.com OR site:community.make.com "doesn\'t work"',
]


class GoogleSearchScraper(BaseScraper):
    """Supplemental web search — uses DuckDuckGo to find complaints across the web."""

    name = "Google"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com {query}',
                f'{query} forum OR community complaint',
                f'{query} broken OR frustrated OR help needed',
            ]
        else:
            queries = COMPLAINT_QUERIES

        return multi_domain_search(queries, "Web Search", limit)
