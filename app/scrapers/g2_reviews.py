from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'g2.com/products reviews "what do you dislike" OR complaint OR problem',
    'g2.com/products salesforce OR hubspot OR jira OR zendesk review complaint',
    'g2.com/products shopify OR quickbooks OR mailchimp OR clickup negative review',
    'g2.com/products asana OR monday OR notion OR freshdesk issue OR problem',
    'g2.com/products "worst thing" OR "doesn\'t work" OR "deal breaker" OR broken',
    'g2.com/products intercom OR pipedrive OR slack complaint OR frustrating',
]


def _label(url):
    if "g2.com" in url:
        return "G2"
    return None


class G2ReviewScraper(BaseScraper):
    """G2 reviews — negative reviews and complaints about business software."""

    name = "G2 Reviews"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'g2.com/products {query} review']
        else:
            queries = QUERIES
        return multi_domain_search(queries, "G2", limit, url_filter=_label)
