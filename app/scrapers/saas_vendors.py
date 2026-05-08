from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'trailhead.salesforce.com error OR issue OR help OR broken',
    'developer.salesforce.com/forums integration OR API OR migration OR deploy',
    'community.hubspot.com "not working" OR broken OR error OR bug',
    'community.hubspot.com integration OR API OR workflow OR custom',
    'community.zendesk.com issue OR broken OR help',
    'community.freshworks.com "not working" OR error OR bug OR help',
    'community.intercom.com issue OR broken OR integration OR API',
    'stripe.com/docs error OR issue OR help integration',
]


def _label(url):
    if "salesforce.com" in url:
        return "Salesforce"
    if "hubspot.com" in url:
        return "HubSpot"
    if "zendesk.com" in url:
        return "Zendesk"
    if "freshworks.com" in url:
        return "Freshworks"
    if "intercom.com" in url:
        return "Intercom"
    if "stripe.com" in url:
        return "Stripe"
    return "SaaS"


class SaaSVendorScraper(BaseScraper):
    """SaaS vendor communities — Salesforce, HubSpot, Zendesk, Freshworks users with issues."""

    name = "SaaS Vendors"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'trailhead.salesforce.com {query}',
                f'community.hubspot.com {query}',
                f'community.zendesk.com {query}',
                f'community.freshworks.com {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "SaaS", limit, url_filter=_label)
