"""
Upwork scraper — finds Upwork job listings via DuckDuckGo search.
Upwork killed their RSS feeds, so we search for recent job posts instead.

Author: Howell Brady | Origin: BonnieTheDog420
"""

from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Upwork job listings — people literally paying for dev work
    'site:upwork.com/freelance-jobs fix bug integration',
    'site:upwork.com/freelance-jobs api integration webhook',
    'site:upwork.com/freelance-jobs automation script bot',
    'site:upwork.com/freelance-jobs data migration import export',
    'site:upwork.com/freelance-jobs broken fix repair software',
    # Reddit discussions about Upwork projects
    'site:reddit.com/r/Upwork client project integration OR fix OR build',
]


def _label(url):
    if "upwork.com" in url:
        return "Upwork"
    if "reddit.com" in url:
        return "Upwork/Reddit"
    return "Upwork"


class UpworkScraper(BaseScraper):
    """Upwork job listings — people literally paying for dev work."""

    name = "Upwork Jobs"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:upwork.com/freelance-jobs {query}',
                f'site:reddit.com/r/Upwork {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Upwork", limit, url_filter=_label)
