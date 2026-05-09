from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Quora
    'site:quora.com software broken integration fix',
    'site:quora.com software "not working" OR broken OR "best alternative to" help',
    'site:quora.com "frustrated with" OR "problems with" software OR SaaS',
    'site:quora.com "how to fix" OR "how to automate" business OR workflow',
    'site:quora.com "need developer" OR "hire freelancer" software OR tool',
    'site:quora.com "small business" software broken OR issue OR help',
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
            queries = [
                f'site:quora.com {query} software broken fix',
                f'site:quora.com {query} software help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Quora", limit, url_filter=_label)
