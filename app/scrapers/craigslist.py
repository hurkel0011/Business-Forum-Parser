from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Reddit discussions
    'site:reddit.com need developer fix software small business',
    'site:reddit.com need developer fix website OR app OR integration',
    'site:reddit.com "looking for developer" OR "need programmer" fix OR build OR automate',
    'site:reddit.com small business software fix OR repair OR build hire',
    # Site-targeted: Reddit forhire and gig queries
    'site:reddit.com/r/forhire developer fix OR build OR automate project',
    'site:reddit.com "need developer" OR "need programmer" fix OR build OR repair website OR software',
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
            queries = [
                f'site:reddit.com need developer {query} fix small business',
                f'Craigslist {query} developer fix project',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Craigslist", limit, url_filter=_label)
