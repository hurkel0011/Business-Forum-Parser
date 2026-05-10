from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Reddit — best source for real user complaints
    'site:reddit.com Salesforce integration broken OR error OR "not working"',
    'site:reddit.com HubSpot integration broken OR error OR "not working"',
    'site:reddit.com Zendesk integration broken OR error OR "not working"',
    'site:reddit.com Freshworks OR Freshdesk error OR broken OR frustrated',
    'site:reddit.com Intercom error OR broken OR integration issue',
    'site:reddit.com Stripe webhook error OR integration OR "not working"',
    # Official community forums (NOT docs/KB)
    'site:trailblazer.salesforce.com error OR broken OR integration',
    'site:community.hubspot.com error OR broken OR integration',
    # StackOverflow
    'site:stackoverflow.com Salesforce API integration error',
    'site:stackoverflow.com HubSpot OR Zendesk OR Stripe API error',
]


def _label(url):
    if "salesforce.com" in url:
        return "Salesforce"
    if "hubspot.com" in url:
        return "HubSpot"
    if "zendesk.com" in url:
        return "Zendesk"
    if "freshworks.com" in url or "freshdesk.com" in url:
        return "Freshworks"
    if "intercom.com" in url:
        return "Intercom"
    if "stripe.com" in url:
        return "Stripe"
    if "reddit.com" in url:
        return "SaaS"
    if "stackoverflow.com" in url:
        return "SaaS"
    return "SaaS"


class SaaSVendorScraper(BaseScraper):
    """SaaS vendor communities — Salesforce, HubSpot, Zendesk, Freshworks users with issues."""

    name = "SaaS Vendors"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com Salesforce {query}',
                f'site:reddit.com HubSpot {query}',
                f'site:reddit.com Zendesk OR Stripe {query}',
                f'site:community.hubspot.com {query}',
                f'site:trailblazer.salesforce.com {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "SaaS", limit, url_filter=_label)
