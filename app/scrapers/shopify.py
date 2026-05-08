from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'community.shopify.com "need help" OR broken OR "not working" theme OR app',
    'community.shopify.com "custom code" OR "hire developer" OR "need someone to"',
    'community.shopify.com checkout OR payment OR shipping issue OR error OR broken',
    'community.shopify.com migrate OR "moving from" OR "switch to shopify"',
    'community.shopify.com speed OR slow OR SEO OR conversion fix OR help',
    'community.shopify.com integration OR API OR "app doesn\'t" OR sync problem',
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
            queries = [f'community.shopify.com {query}']
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Shopify", limit, url_filter=_label)
