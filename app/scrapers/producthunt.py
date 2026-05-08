from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'producthunt.com "alternative to" OR "better than" OR "replacement for"',
    'producthunt.com frustrated OR broken OR "doesn\'t work"',
    'producthunt.com "need a tool" OR "looking for" OR "anyone built"',
    'producthunt.com complaint OR problem OR issue OR "not working"',
    'producthunt.com developer OR automation OR integration help',
]


def _label(url):
    if "producthunt.com" in url:
        return "ProductHunt"
    return None


class ProductHuntScraper(BaseScraper):
    """Product Hunt discussions — complaints about existing tools, feature requests."""

    name = "Product Hunt"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'producthunt.com {query}']
        else:
            queries = QUERIES
        return multi_domain_search(queries, "ProductHunt", limit, url_filter=_label)
