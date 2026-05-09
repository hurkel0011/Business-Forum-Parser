"""
DuckDuckGo-powered primary search scraper.
Uses the ddgs package for reliable search without CAPTCHAs.

Author: Howell Brady | Origin: BonnieTheDog420
"""

from .base import BaseScraper
from .search_util import multi_domain_search

# Very specific complaint-focused search queries
COMPLAINT_QUERIES = [
    # Reddit pain signals
    'site:reddit.com "frustrated with" OR "completely broken" software',
    'site:reddit.com "help needed" OR "losing money" OR "critical bug" software',
    'site:reddit.com "integration broken" OR "API not working" OR "sync failed"',
    'site:reddit.com "workflow broken" OR "automation failed" business',
    'site:reddit.com "switching from" OR "looking for alternative" software tool',
    'site:reddit.com "need developer" OR "hire someone" OR "willing to pay" fix',
    'site:reddit.com "production issue" OR "data loss" OR "migration failed"',

    # Specific product complaints
    'site:reddit.com salesforce "not working" OR "broken" OR "frustrated"',
    'site:reddit.com hubspot OR zendesk OR jira "bug" OR "issue" OR "broken"',
    'site:reddit.com shopify "can\'t" OR "broken" OR "need help"',
    'site:reddit.com quickbooks OR xero integration OR export problem',

    # Automation gaps
    'site:reddit.com "no integration" OR "manual process" OR "spreadsheet" automate',
    'site:reddit.com "zapier can\'t" OR "automation doesn\'t" OR "need custom"',

    # Stack Overflow unanswered
    'site:stackoverflow.com unanswered business OR enterprise integration',
]


class DuckDuckGoScraper(BaseScraper):
    """Primary web search — uses DuckDuckGo to find complaints across the web."""

    name = "Web Search"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com {query}',
                f'{query} community forum complaint',
                f'{query} broken OR frustrated OR help needed',
            ]
        else:
            queries = COMPLAINT_QUERIES

        return multi_domain_search(queries, "Web Search", limit)
