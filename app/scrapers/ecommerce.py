from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Reddit discussions
    'site:reddit.com WooCommerce error OR broken OR "not working" OR help',
    'site:reddit.com BigCommerce error OR broken OR "not working" OR help',
    'site:reddit.com Magento error OR broken OR crash OR "not working" help',
    'site:reddit.com Wix ecommerce OR store error OR broken OR "not working" help',
    'site:reddit.com Squarespace store OR ecommerce error OR broken help',
    # General complaint queries
    'WooCommerce community error plugin checkout help',
    'BigCommerce community error integration help',
    'Magento community error extension migration help',
    'Wix ecommerce community error broken help',
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
    return "eCommerce"


class EcommerceScraper(BaseScraper):
    """eCommerce platform forums — BigCommerce, WooCommerce, Magento, Squarespace, Wix."""

    name = "eCommerce Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com WooCommerce OR BigCommerce OR Magento {query}',
                f'site:reddit.com Wix OR Squarespace ecommerce {query}',
                f'WooCommerce OR BigCommerce OR Magento {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "eCommerce", limit, url_filter=_label)
