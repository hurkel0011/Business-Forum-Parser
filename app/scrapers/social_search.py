from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # LinkedIn — business decision makers with tool pain
    'site:linkedin.com integration broken OR nightmare OR "not working"',
    'site:linkedin.com CRM migration OR switching OR frustrated',
    'site:linkedin.com "broken workflow" OR "broken automation" OR "broken integration"',
    'site:linkedin.com Salesforce OR HubSpot OR Zendesk broken OR migration',
    # Reddit — direct complaints
    'site:reddit.com SaaS broken frustrated "need help" switching',
    'site:reddit.com software broken "looking for developer" OR "hire someone"',
    'site:reddit.com smallbusiness OR entrepreneur software broken OR "not working"',
    'site:reddit.com webdev freelance "client needs" OR "looking for" project',
]


def _label(url):
    if "facebook.com" in url:
        return "Facebook"
    if "linkedin.com" in url:
        return "LinkedIn"
    if "twitter.com" in url or "x.com" in url:
        return "Twitter/X"
    if "reddit.com" in url:
        return "Reddit"
    return "Social"


class SocialMediaScraper(BaseScraper):
    """Search Facebook groups, Twitter/X, LinkedIn, and Reddit."""

    name = "Social Media"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com {query} software broken frustrated help',
                f'site:reddit.com {query} hire OR need developer help',
                f'site:linkedin.com {query} software broken help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Social", limit, url_filter=_label)
