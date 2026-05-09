from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: official community forums
    'site:trailblazer.salesforce.com error OR broken OR integration OR help',
    'site:community.hubspot.com error OR broken OR integration OR help',
    'site:support.zendesk.com error OR broken OR integration OR help',
    # Site-targeted: Reddit discussions
    'site:reddit.com Salesforce error OR broken OR "not working" OR integration help',
    'site:reddit.com HubSpot error OR broken OR "not working" OR integration help',
    'site:reddit.com Zendesk error OR broken OR "not working" OR help',
    'site:reddit.com Freshworks OR Freshdesk error OR broken OR help',
    'site:reddit.com Intercom error OR broken OR integration OR help',
    'site:reddit.com Stripe integration OR error OR webhook OR "not working" help',
    # StackOverflow
    'site:stackoverflow.com Salesforce API integration error',
    'site:stackoverflow.com HubSpot API integration error',
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
    return "SaaS"


class SaaSVendorScraper(BaseScraper):
    """SaaS vendor communities — Salesforce, HubSpot, Zendesk, Freshworks users with issues."""

    name = "SaaS Vendors"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com Salesforce {query}',
                f'site:community.hubspot.com {query}',
                f'site:trailblazer.salesforce.com {query}',
                f'Salesforce OR HubSpot OR Zendesk {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "SaaS", limit, url_filter=_label)
