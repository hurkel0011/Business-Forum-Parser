from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'craigslist.org fix OR build OR develop website OR software OR app',
    'craigslist.org "computer gigs" OR "web design" fix OR automate OR build',
    'craigslist.org developer OR programmer OR coder hire OR need OR freelance',
    'craigslist.org automation OR integration OR scraping OR script OR bot',
    'craigslist.org "web developer" OR "software developer" OR "app developer" needed',
]


def _label(url):
    if "craigslist.org" in url:
        return "Craigslist"
    return None


class CraigslistScraper(BaseScraper):
    """Craigslist computer gigs — people posting freelance work requests."""

    name = "Craigslist Gigs"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'craigslist.org {query}']
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Craigslist", limit, url_filter=_label)
