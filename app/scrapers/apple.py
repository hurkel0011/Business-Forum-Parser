from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: official developer forums
    'site:developer.apple.com/forums error OR crash OR broken OR bug help',
    'site:developer.apple.com/forums Xcode OR API OR SDK OR framework issue help',
    'site:developer.apple.com/forums migration OR provisioning OR deployment issue help',
    # Site-targeted: Reddit discussions
    'site:reddit.com iOS development error OR crash OR broken OR bug help',
    'site:reddit.com Xcode error OR crash OR broken OR "not working" help',
    'site:reddit.com Apple developer API OR SDK OR framework issue help',
    'site:reddit.com Apple enterprise MDM OR deployment OR provisioning error help',
    # Site-targeted: StackOverflow
    'site:reddit.com Xcode error OR crash OR "build failed" OR broken help',
    'site:reddit.com Swift OR SwiftUI error OR crash OR broken help',
]


def _label(url):
    if "developer.apple" in url:
        return "Apple Developer"
    if "apple.com" in url:
        return "Apple Support"
    if "reddit.com" in url:
        return "Apple"
    return "Apple"


class AppleScraper(BaseScraper):
    """Apple Support & Developer Forums — users with software, migration, and automation issues."""

    name = "Apple Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:developer.apple.com/forums {query}',
                f'site:reddit.com iOS development OR Xcode OR Apple {query}',
                f'Apple developer {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Apple", limit, url_filter=_label)
