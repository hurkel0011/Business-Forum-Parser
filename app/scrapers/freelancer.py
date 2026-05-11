from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Reddit discussions
    'site:reddit.com freelance software project help needed',
    'site:reddit.com freelance developer fix OR repair OR debug website OR software',
    'site:reddit.com freelance automation OR integration OR custom tool build project',
    'site:reddit.com freelance migration OR convert OR transfer data project',
    'site:reddit.com freelance urgent developer OR programmer hire project',
    # Site-targeted: more Reddit freelance queries
    'site:reddit.com/r/forhire freelance developer fix OR build OR debug project',
    'site:reddit.com freelance developer needed software OR integration OR automation project',
]


def _label(url):
    if "freelancer.com" in url:
        return "Freelancer.com"
    if "reddit.com" in url:
        return "Freelancer"
    return "Freelancer"


class FreelancerScraper(BaseScraper):
    """Freelancer.com project listings — clients posting jobs with budgets."""

    name = "Freelancer.com"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com freelance {query} developer project help',
                f'Freelancer.com {query} development project',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Freelancer.com", limit, url_filter=_label)
