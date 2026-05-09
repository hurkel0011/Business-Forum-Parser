from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: official community forum
    'site:community.shopify.com error OR broken OR "not working" OR help',
    'site:community.shopify.com app OR theme error OR broken OR issue',
    'site:community.shopify.com checkout OR payment OR shipping error OR issue',
    'site:community.shopify.com integration OR API OR sync error OR broken',
    # Site-targeted: Reddit discussions
    'site:reddit.com Shopify error OR broken OR "not working" OR help',
    'site:reddit.com Shopify app OR theme OR checkout broken OR error help',
    'site:reddit.com Shopify migration OR "moving from" OR "switch to" help',
    # General complaint queries
    'Shopify community error broken help',
    'Shopify community integration API help',
]


def _label(url):
    if "community.shopify.com" in url:
        return "Shopify"
    return None


class ShopifyScraper(BaseScraper):
    """Shopify Community forums — merchants needing dev help with their stores."""

    name = "Shopify Community"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:community.shopify.com {query}',
                f'site:reddit.com Shopify {query}',
                f'Shopify {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Shopify", limit, url_filter=_label)
