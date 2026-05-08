from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'capterra.com reviews salesforce OR hubspot OR jira OR zendesk complaint',
    'capterra.com reviews shopify OR quickbooks OR mailchimp OR clickup negative',
    'capterra.com reviews "cons" OR "disadvantages" OR "worst" OR "doesn\'t work"',
    'capterra.com reviews asana OR monday OR notion OR freshdesk problem',
    'capterra.com reviews wix OR squarespace OR pipedrive OR zoho issue',
    'capterra.com reviews "not recommended" OR terrible OR frustrating OR broken',
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
            queries = [f'capterra.com reviews {query}']
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Capterra", limit, url_filter=_label)
