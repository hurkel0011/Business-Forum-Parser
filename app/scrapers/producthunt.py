from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Product Hunt
    'site:producthunt.com discussion error OR broken OR "doesn\'t work" alternative',
    'site:producthunt.com "alternative to" OR "better than" OR "replacement for" tool',
    'site:producthunt.com "need a tool" OR "looking for" OR "anyone built" help',
    'site:producthunt.com complaint OR problem OR issue OR "not working" feedback',
    'site:producthunt.com developer OR automation OR integration help feedback',
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
            queries = [
                f'site:producthunt.com {query} discussion feedback',
                f'site:producthunt.com {query} alternative problem',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "ProductHunt", limit, url_filter=_label)
