from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Reddit discussions (no major public community forums for healthcare IT)
    'site:reddit.com "Epic EHR" OR "Epic Systems" error OR broken OR integration help',
    'site:reddit.com Cerner OR "Oracle Health" error OR broken OR integration help',
    'site:reddit.com eClinicalWorks error OR broken OR "not working" help',
    'site:reddit.com Athenahealth error OR broken OR integration help',
    'site:reddit.com EHR OR EMR integration OR migration OR "not working" help',
    'site:reddit.com HL7 OR FHIR integration OR error OR broken help',
    # Site-targeted: more Reddit healthcare IT queries
    'site:reddit.com "Epic EHR" OR "Epic Systems" integration OR migration OR workaround help',
    'site:reddit.com Cerner OR "Oracle Health" integration OR migration OR workaround help',
    'site:reddit.com eClinicalWorks broken OR workaround OR migration help',
    'site:reddit.com Athenahealth broken OR integration OR workaround help',
]


def _label(url):
    if "epic.com" in url:
        return "Epic"
    if "cerner" in url or "oracle" in url.lower():
        return "Cerner"
    if "healthit.gov" in url:
        return "HealthIT.gov"
    return "Healthcare IT"


class HealthcareITScraper(BaseScraper):
    """Healthcare IT forums — Epic, Cerner, EHR/EMR users needing integrations and fixes."""

    name = "Healthcare IT"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com "Epic EHR" OR Cerner OR eClinicalWorks {query}',
                f'site:reddit.com EHR OR EMR {query} integration help',
                f'Epic OR Cerner OR Athenahealth {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Healthcare IT", limit, url_filter=_label)
