from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Trustpilot
    'site:trustpilot.com software review broken OR terrible OR "doesn\'t work"',
    'site:trustpilot.com SaaS review broken OR terrible OR awful',
    'site:trustpilot.com hosting OR CRM review broken OR "not working" OR issue',
    'site:trustpilot.com Shopify OR Wix OR Squarespace review broken OR issue',
    'site:trustpilot.com QuickBooks OR Xero OR Mailchimp review broken OR issue',
    'site:trustpilot.com "1 star" OR terrible OR avoid software review',
]


def _label(url):
    if "trustpilot.com" in url:
        return "Trustpilot"
    return None


class TrustpilotScraper(BaseScraper):
    """Trustpilot reviews — low-star complaints about B2B software."""

    name = "Trustpilot"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:trustpilot.com {query} review broken terrible',
                f'site:trustpilot.com {query} software review issue',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Trustpilot", limit, url_filter=_label)
