from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'trustpilot.com/review software terrible OR broken OR scam OR "doesn\'t work"',
    'trustpilot.com/review hosting OR saas OR crm OR "not working" OR awful',
    'trustpilot.com/review salesforce OR hubspot OR zendesk OR atlassian complaint',
    'trustpilot.com/review shopify OR wix OR squarespace OR godaddy issue',
    'trustpilot.com/review quickbooks OR xero OR mailchimp OR stripe problem',
    'trustpilot.com/review "1 star" OR terrible OR avoid OR worst software',
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
            queries = [f'trustpilot.com/review {query}']
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Trustpilot", limit, url_filter=_label)
