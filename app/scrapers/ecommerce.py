from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'community.bigcommerce.com help OR issue OR broken OR error',
    'wordpress.org/support/plugin/woocommerce "not working" OR broken OR error OR help',
    'wordpress.org/support/plugin/woocommerce payment OR checkout OR shipping issue',
    'community.magento.com issue OR error OR help OR broken OR fix',
    'prestashop.com/forums help OR error OR broken OR issue OR bug',
    'forum.squarespace.com "not working" OR broken OR help OR "custom code"',
    'forum.squarespace.com developer OR CSS OR JavaScript OR integration',
    'community.wix.com help OR broken OR issue OR "not working" OR bug',
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
                f'community.bigcommerce.com {query}',
                f'wordpress.org/support/plugin/woocommerce {query}',
                f'community.magento.com {query}',
                f'forum.squarespace.com {query}',
                f'community.wix.com {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "eCommerce", limit, url_filter=_label)
