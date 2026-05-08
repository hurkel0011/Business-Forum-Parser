from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'freelancer.com/projects fix OR repair OR debug website OR software OR app',
    'freelancer.com/projects build OR develop OR create automation OR integration OR tool',
    'freelancer.com/projects migrate OR convert OR transfer data OR website OR database',
    'freelancer.com/projects API OR integration OR webhook OR sync OR connector',
    'freelancer.com/projects urgent OR ASAP OR immediately developer OR programmer',
    'freelancer.com/projects scraping OR automation OR bot OR script',
]


def _label(url):
    if "freelancer.com" in url:
        return "Freelancer.com"
    return None


class FreelancerScraper(BaseScraper):
    """Freelancer.com project listings — clients posting jobs with budgets."""

    name = "Freelancer.com"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'freelancer.com/projects {query}']
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Freelancer.com", limit, url_filter=_label)
