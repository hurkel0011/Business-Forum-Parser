from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'quickbooks.intuit.com/learn-support "not working" OR error OR broken OR help',
    'quickbooks.intuit.com/learn-support integration OR import OR export OR sync',
    'central.xero.com issue OR error OR broken OR help OR integration',
    'support.freshbooks.com issue OR "not working" OR help OR integration',
    'support.waveapps.com issue OR "not working" OR help OR integration',
    'communityhub.sage.com error OR issue OR help OR "not working"',
    '"accounting software" "not working" OR broken OR "need help" integration OR migration',
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
                f'quickbooks.intuit.com {query}',
                f'central.xero.com {query}',
                f'communityhub.sage.com {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Accounting", limit, url_filter=_label)
