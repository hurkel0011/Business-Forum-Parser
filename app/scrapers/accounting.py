from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Reddit — accounting software pain
    'site:reddit.com QuickBooks error OR broken OR "not working" OR frustrated',
    'site:reddit.com QuickBooks integration OR sync OR import failed',
    'site:reddit.com Xero error OR broken OR "not working" OR sync issue',
    'site:reddit.com Xero integration OR API OR "bank feed" broken',
    'site:reddit.com FreshBooks error OR broken OR "not working"',
    'site:reddit.com Sage accounting error OR broken OR migration',
    # StackOverflow
    'site:stackoverflow.com QuickBooks API integration error',
    'site:stackoverflow.com Xero API integration error',
    # Official community
    'site:quickbooks.intuit.com community error integration',
]


def _label(url):
    if "quickbooks" in url or "intuit.com" in url:
        return "QuickBooks"
    if "xero.com" in url:
        return "Xero"
    if "freshbooks.com" in url:
        return "FreshBooks"
    if "waveapps.com" in url:
        return "Wave"
    if "sage.com" in url:
        return "Sage"
    if "reddit.com" in url:
        return "Accounting"
    if "stackoverflow.com" in url:
        return "Accounting"
    return "Accounting"


class AccountingScraper(BaseScraper):
    """Accounting/finance software forums — QuickBooks, Xero, Sage users with integration issues."""

    name = "Accounting Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com QuickBooks {query}',
                f'site:reddit.com Xero OR FreshBooks {query}',
                f'site:stackoverflow.com QuickBooks OR Xero {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Accounting", limit, url_filter=_label)
