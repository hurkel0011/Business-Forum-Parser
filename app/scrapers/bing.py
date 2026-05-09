"""
DuckDuckGo-powered general search scraper.
Kept as 'bing.py' for backward compat (was originally Bing, now uses DDG).

Author: Howell Brady | Origin: BonnieTheDog420
"""

from .base import BaseScraper
from .search_util import multi_domain_search

COMPLAINT_QUERIES = [
    'site:reddit.com "frustrated with" OR "completely broken" software',
    'site:reddit.com "integration broken" OR "API not working" OR "sync failed"',
    'site:reddit.com "need developer" OR "willing to pay" OR "hire someone" fix',
    'site:reddit.com "switching from" OR "looking for alternative" software',
    'site:reddit.com "workflow broken" OR "manual process" OR "automation failed"',
    'site:reddit.com "production down" OR "critical bug" OR "urgent fix"',
    '"can\'t export" OR "data migration" OR "import broken" help forum',
    'salesforce OR hubspot OR zendesk "broken" OR "frustrated" community',
    'shopify OR quickbooks OR jira "bug" OR "not working" community',
    '"no integration" OR "need custom" OR "spreadsheet" automate community',
]


class BingSearchScraper(BaseScraper):
    """General web search — uses DuckDuckGo to find complaints across the web."""

    name = "Bing/Edge"

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
