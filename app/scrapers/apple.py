from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'discussions.apple.com "data migration" OR transfer OR "lost files" OR backup',
    'discussions.apple.com "app doesn\'t work" OR crash OR bug OR broken',
    'discussions.apple.com automation OR shortcut OR script OR Automator',
    'discussions.apple.com enterprise OR MDM OR deployment OR management',
    'developer.apple.com/forums API OR integration OR bug OR workaround',
    'developer.apple.com/forums help OR issue OR error OR crash OR rejected',
]


def _label(url):
    if "developer.apple" in url:
        return "Apple Developer"
    if "apple.com" in url:
        return "Apple Support"
    return None


class AppleScraper(BaseScraper):
    """Apple Support & Developer Forums — users with software, migration, and automation issues."""

    name = "Apple Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'discussions.apple.com {query}',
                f'developer.apple.com/forums {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Apple", limit, url_filter=_label)
