from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'community.spiceworks.com "need help" OR "looking for" software OR tool OR solution',
    'community.spiceworks.com migration OR upgrade OR replace server OR software',
    'community.spiceworks.com broken OR "not working" OR error OR crash application',
    'community.spiceworks.com automate OR script OR powershell OR deploy',
    'community.spiceworks.com integration OR sync OR connect OR API systems',
    'community.spiceworks.com recommend OR "alternative to" OR "better than" software',
]


def _label(url):
    if "spiceworks.com" in url:
        return "Spiceworks"
    return None


class SpiceworksScraper(BaseScraper):
    """Spiceworks IT Community — sysadmins and IT pros with enterprise tool problems."""

    name = "Spiceworks"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'community.spiceworks.com {query}']
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Spiceworks", limit, url_filter=_label)
