from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Capterra
    'site:capterra.com review software broken OR "doesn\'t work" OR complaint',
    'site:capterra.com review "cons" OR "disadvantages" OR "worst" software',
    'site:capterra.com review Salesforce OR HubSpot OR Jira complaint OR negative',
    'site:capterra.com review Shopify OR QuickBooks OR Mailchimp issue OR negative',
    'site:capterra.com review Wix OR Squarespace OR Pipedrive issue OR problem',
    'site:capterra.com review "not recommended" OR terrible OR frustrating software',
]


def _label(url):
    if "capterra.com" in url:
        return "Capterra"
    return None


class CapterraScraper(BaseScraper):
    """Capterra software reviews — complaints about business tools."""

    name = "Capterra"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:capterra.com {query} review broken issue',
                f'site:capterra.com {query} review complaint problem',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Capterra", limit, url_filter=_label)
