from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'wordpress.org/support help OR broken OR "not working" plugin OR theme',
    'wordpress.org/support migration OR "moved site" OR "lost data" OR "white screen"',
    'wordpress.org/support "need developer" OR "hire someone" OR "can someone fix"',
    'wordpress.org/support WooCommerce error OR broken OR "doesn\'t work"',
    'wordpress.org/support urgent OR "site down" OR hacked OR malware',
    'wordpress.org/support custom OR modify OR "change functionality" plugin',
]


def _label(url):
    if "wordpress.org" in url:
        return "WordPress"
    return None


class WordPressScraper(BaseScraper):
    """WordPress.org support forums — site owners stuck on broken themes, plugins, migrations."""

    name = "WordPress Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'wordpress.org/support {query}']
        else:
            queries = QUERIES
        return multi_domain_search(queries, "WordPress", limit, url_filter=_label)
