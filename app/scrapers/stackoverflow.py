from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'stackoverflow.com help OR error OR "not working" integration OR API',
    'stackoverflow.com migration OR deployment OR authentication issue',
    'stackoverflow.com automation OR database OR performance problem',
    'superuser.com error OR "not working" OR broken software OR tool',
    'serverfault.com error OR issue OR broken OR migration OR deploy',
    'stackoverflow.com unanswered API OR integration OR automation OR webhook',
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
    """Stack Exchange sites — StackOverflow, SuperUser, ServerFault via Bing search."""

    name = "Stack Overflow"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'stackoverflow.com {query}',
                f'superuser.com {query}',
                f'serverfault.com {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "StackOverflow", limit, url_filter=_label)
