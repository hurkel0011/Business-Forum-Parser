from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'userweb.epic.com error OR issue OR integration OR "not working"',
    '"Epic EHR" OR "Epic Systems" broken OR issue OR integration OR API OR HL7',
    '"Cerner" OR "Oracle Health" "not working" OR broken OR error OR integration',
    'community.healthit.gov issue OR error OR "not working" OR help',
    'reddit.com/r/healthIT broken OR error OR integration OR help OR need',
    '"practice management" OR EHR OR EMR "not working" OR broken OR "need help" integration',
    'HIPAA compliance tool OR software broken OR issue OR need OR help',
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
                f'"EHR" OR "healthcare IT" {query}',
                f'reddit.com/r/healthIT {query}',
                f'"medical software" {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Healthcare IT", limit, url_filter=_label)
