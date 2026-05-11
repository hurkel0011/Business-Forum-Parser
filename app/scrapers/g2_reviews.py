from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: G2
    'site:g2.com review software broken OR "doesn\'t work" OR integration issue',
    'site:g2.com review "what do you dislike" OR complaint OR problem',
    'site:g2.com review Salesforce OR HubSpot OR Jira OR Zendesk complaint',
    'site:g2.com review Shopify OR QuickBooks OR Mailchimp issue OR problem',
    'site:g2.com review "worst thing" OR broken OR avoid software',
    'site:g2.com review Asana OR Monday OR Notion frustrating OR issue',
]


def _label(url):
    if "g2.com" in url:
        return "G2"
    return "G2"


class G2ReviewScraper(BaseScraper):
    """G2 reviews — negative reviews and complaints about business software."""

    name = "G2 Reviews"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:g2.com {query} review complaint issue',
                f'site:g2.com {query} review broken problem',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "G2", limit, url_filter=_label)
