from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'indiehackers.com "need help" OR problem OR issue OR broken software OR tool',
    'indiehackers.com "looking for" developer OR automation OR integration',
    'indiehackers.com "how to" OR "anyone built" OR "alternative to" tool OR saas',
    'indiehackers.com "struggling with" OR "frustrated" OR "can\'t find" software OR platform',
    'indiehackers.com build OR automate OR fix OR migrate product OR business',
]


def _label(url):
    if "indiehackers.com" in url:
        return "IndieHackers"
    return None


class IndieHackersScraper(BaseScraper):
    """IndieHackers community — founders posting about product and tech problems."""

    name = "IndieHackers"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'indiehackers.com {query}']
        else:
            queries = QUERIES
        return multi_domain_search(queries, "IndieHackers", limit, url_filter=_label)
