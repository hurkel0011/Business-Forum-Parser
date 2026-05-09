from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Reddit discussions
    'site:reddit.com QuickBooks error OR broken OR "not working" OR help',
    'site:reddit.com QuickBooks integration OR sync OR import OR export help',
    'site:reddit.com Xero error OR broken OR "not working" OR help',
    'site:reddit.com Xero integration OR sync OR "bank feed" OR API help',
    'site:reddit.com FreshBooks error OR broken OR "not working" OR help',
    # General complaint queries
    'QuickBooks community error integration help',
    'Xero community error sync help',
    'FreshBooks community error invoice help',
    'Sage accounting community error migration help',
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
    return "Accounting"


class AccountingScraper(BaseScraper):
    """Accounting/finance software forums — QuickBooks, Xero, Sage users with integration issues."""

    name = "Accounting Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com QuickBooks OR Xero OR FreshBooks {query}',
                f'QuickBooks OR Xero OR FreshBooks {query} community forum help',
                f'Sage accounting {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Accounting", limit, url_filter=_label)
