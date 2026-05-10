from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Reddit — ecommerce pain
    'site:reddit.com WooCommerce error OR broken OR "not working" OR plugin',
    'site:reddit.com WooCommerce checkout OR payment OR shipping broken',
    'site:reddit.com BigCommerce error OR broken OR "not working" OR integration',
    'site:reddit.com Magento error OR broken OR crash OR performance',
    'site:reddit.com Wix ecommerce OR store error OR broken',
    'site:reddit.com Squarespace ecommerce error OR broken OR "not working"',
    # StackOverflow
    'site:stackoverflow.com WooCommerce plugin error broken',
    'site:stackoverflow.com Magento error integration API',
    # Official communities
    'site:community.bigcommerce.com error OR broken OR integration',
]


def _label(url):
    if "bigcommerce.com" in url:
        return "BigCommerce"
    if "woocommerce" in url:
        return "WooCommerce"
    if "magento.com" in url:
        return "Magento"
    if "squarespace.com" in url:
        return "Squarespace"
    if "prestashop.com" in url:
        return "PrestaShop"
    if "wix.com" in url:
        return "Wix"
    if "reddit.com" in url:
        return "eCommerce"
    if "stackoverflow.com" in url:
        return "eCommerce"
    return "eCommerce"


class EcommerceScraper(BaseScraper):
    """eCommerce platform forums — BigCommerce, WooCommerce, Magento, Squarespace, Wix."""

    name = "eCommerce Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com WooCommerce {query}',
                f'site:reddit.com BigCommerce OR Magento {query}',
                f'site:stackoverflow.com WooCommerce OR Magento {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "eCommerce", limit, url_filter=_label)
