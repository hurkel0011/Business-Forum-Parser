from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Reddit discussions
    'site:reddit.com "real estate CRM" error OR broken OR "not working" help',
    'site:reddit.com kvCORE error OR broken OR integration OR help',
    'site:reddit.com Propertybase error OR broken OR integration OR help',
    'site:reddit.com Zillow OR Realtor.com API OR integration OR error help',
    'site:reddit.com MLS OR IDX integration OR "not working" OR broken OR error help',
    # Site-targeted: more Reddit real estate tech queries
    'site:reddit.com kvCORE broken OR integration OR sync OR error help',
    'site:reddit.com Propertybase broken OR integration OR sync OR error help',
    'site:reddit.com "real estate" software OR CRM broken OR error OR workaround help',
    'site:reddit.com MLS OR IDX integration OR sync OR broken OR error help',
]


def _label(url):
    if "appfolio" in url:
        return "AppFolio"
    if "buildium" in url:
        return "Buildium"
    if "followupboss" in url:
        return "Follow Up Boss"
    if "kvcore" in url:
        return "kvCORE"
    if "zillow" in url:
        return "Zillow"
    return "PropTech"


class RealEstateTechScraper(BaseScraper):
    """PropTech/Real estate tech — property management, real estate CRM, MLS integration issues."""

    name = "Real Estate Tech"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com "real estate CRM" OR kvCORE OR Propertybase {query}',
                f'site:reddit.com MLS OR IDX {query} integration help',
                f'real estate tech {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "PropTech", limit, url_filter=_label)
