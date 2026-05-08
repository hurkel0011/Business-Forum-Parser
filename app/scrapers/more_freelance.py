from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'fiverr.com fix OR repair OR debug website OR software OR app',
    'fiverr.com build OR automate OR integrate OR migrate OR scrape',
    'fiverr.com urgent OR ASAP developer OR programmer OR coder',
    'peopleperhour.com fix OR build OR develop OR automate website OR software',
    'peopleperhour.com API OR integration OR migration OR database',
    'guru.com/jobs fix OR repair OR debug OR develop software OR website',
    'guru.com/jobs automation OR integration OR migration OR scraping',
    'bark.com "web developer" OR "software developer" OR "app developer"',
]


def _label(url):
    if "fiverr.com" in url:
        return "Fiverr"
    if "peopleperhour.com" in url:
        return "PeoplePerHour"
    if "guru.com" in url:
        return "Guru"
    if "bark.com" in url:
        return "Bark"
    return "Freelance"


class MoreFreelanceScraper(BaseScraper):
    """Additional freelance platforms — Fiverr, PeoplePerHour, Guru, Bark."""

    name = "More Freelance"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'fiverr.com {query}',
                f'peopleperhour.com {query}',
                f'guru.com {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Freelance", limit, url_filter=_label)
