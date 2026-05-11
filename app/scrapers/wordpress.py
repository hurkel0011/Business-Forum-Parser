from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: official community forums
    'site:wordpress.org/support plugin error OR broken OR "not working" help',
    'site:wordpress.org/support theme error OR broken OR "not working" help',
    'site:wordpress.org/support migration OR "white screen" OR crash help',
    'site:wordpress.org/support hacked OR malware OR security issue help',
    # Site-targeted: Reddit discussions
    'site:reddit.com WordPress error OR broken OR "not working" OR help',
    'site:reddit.com WooCommerce error OR broken OR "not working" OR help',
    'site:reddit.com WordPress plugin OR theme broken OR error help',
    'site:reddit.com Elementor error OR broken OR "not working" help',
    # Site-targeted: more WordPress queries
    'site:wordpress.org/support WooCommerce OR checkout OR payment error help',
    'site:reddit.com WooCommerce checkout OR payment OR shipping error help',
    'site:reddit.com Elementor broken OR error OR crash OR "not working" help',
]


def _label(url):
    if "wordpress.org" in url:
        return "WordPress"
    if "reddit.com" in url:
        return "WordPress"
    return "WordPress"


class WordPressScraper(BaseScraper):
    """WordPress.org support forums — site owners stuck on broken themes, plugins, migrations."""

    name = "WordPress Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:wordpress.org/support {query}',
                f'site:reddit.com WordPress OR WooCommerce OR Elementor {query}',
                f'WordPress OR WooCommerce {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "WordPress", limit, url_filter=_label)
