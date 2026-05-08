from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'quora.com "best alternative to" software OR saas OR tool',
    'quora.com "frustrated with" OR "problems with" software business',
    'quora.com "how to fix" OR "how to automate" business process workflow',
    'quora.com "need developer" OR "hire freelancer" OR "build a tool"',
    'quora.com "data migration" OR "integration problem" OR "API issue" business',
    'quora.com "small business" software "doesn\'t work" OR broken OR issue',
]


def _label(url):
    if "quora.com" in url:
        return "Quora"
    return None


class QuoraScraper(BaseScraper):
    """Quora questions — business owners asking about problems."""

    name = "Quora"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'quora.com {query}']
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Quora", limit, url_filter=_label)
