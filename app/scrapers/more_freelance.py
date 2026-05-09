from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Reddit discussions
    'site:reddit.com hiring developer fix integration',
    'site:reddit.com hiring developer fix OR repair OR debug software OR website',
    'site:reddit.com hiring developer build OR automate OR integrate OR migrate',
    'site:reddit.com hiring developer urgent OR ASAP project',
    # General complaint queries
    'Fiverr fix OR repair OR debug website OR software project',
    'Fiverr build OR automate OR integrate coding project',
    'PeoplePerHour fix OR build OR develop website OR software project',
    'Guru fix OR develop OR automate software project',
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
                f'site:reddit.com hiring developer {query} fix integration',
                f'Fiverr OR PeoplePerHour OR Guru {query} development project',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Freelance", limit, url_filter=_label)
