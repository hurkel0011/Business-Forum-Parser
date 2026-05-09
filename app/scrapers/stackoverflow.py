from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: StackOverflow
    'site:stackoverflow.com integration error broken help',
    'site:stackoverflow.com API error OR "not working" OR broken help',
    'site:stackoverflow.com migration OR deployment error OR issue help',
    'site:stackoverflow.com automation OR webhook OR plugin error help',
    'site:stackoverflow.com authentication OR database OR performance issue help',
    # Site-targeted: other Stack Exchange sites
    'site:superuser.com software error OR broken OR "not working" help',
    'site:serverfault.com server OR deploy OR migration error help',
]


def _label(url):
    if "stackoverflow.com" in url:
        return "StackOverflow"
    if "superuser.com" in url:
        return "SuperUser"
    if "serverfault.com" in url:
        return "ServerFault"
    if "stackexchange.com" in url:
        return "StackExchange"
    return "StackOverflow"


class StackOverflowScraper(BaseScraper):
    """Stack Exchange sites — StackOverflow, SuperUser, ServerFault."""

    name = "Stack Overflow"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:stackoverflow.com {query} error help',
                f'site:stackoverflow.com {query} integration issue',
                f'site:superuser.com {query} error help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "StackOverflow", limit, url_filter=_label)
