from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Indie Hackers
    'site:indiehackers.com integration broken help',
    'site:indiehackers.com problem OR issue OR "need help" software OR tool',
    'site:indiehackers.com "struggling with" OR frustrated OR broken OR stuck help',
    'site:indiehackers.com "looking for" developer OR automation OR integration help',
    'site:indiehackers.com "how to" OR "anyone built" OR "alternative to" tool OR SaaS',
    'site:indiehackers.com build OR automate OR fix OR migrate product OR business',
]


def _label(url):
    if "indiehackers.com" in url:
        return "IndieHackers"
    return "IndieHackers"


class IndieHackersScraper(BaseScraper):
    """IndieHackers community — founders posting about product and tech problems."""

    name = "IndieHackers"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:indiehackers.com {query} problem help',
                f'site:indiehackers.com {query} integration broken',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "IndieHackers", limit, url_filter=_label)
