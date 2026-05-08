from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    '"AppFolio" OR "Buildium" OR "Rent Manager" "not working" OR broken OR error OR integration',
    '"property management software" "not working" OR broken OR "need help" integration OR automation',
    '"Follow Up Boss" OR "kvCORE" OR "BoomTown" "not working" OR broken OR integration OR error',
    '"real estate CRM" broken OR "not working" OR issue OR "need help" integration OR API',
    'MLS OR IDX integration OR "not working" OR broken OR error OR feed',
    'Zillow OR Realtor.com API OR integration OR "not working" OR broken OR sync',
    '"proptech" OR "real estate technology" issue OR broken OR "not working" OR need',
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
                f'"property management" OR "real estate" {query}',
                f'MLS OR IDX {query}',
                f'"proptech" {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "PropTech", limit, url_filter=_label)
