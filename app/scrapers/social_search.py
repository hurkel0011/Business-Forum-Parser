from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Reddit discussions
    'site:reddit.com SaaS broken frustrated switching',
    'site:reddit.com software broken frustrated "need help" OR "looking for" fix',
    'site:reddit.com smallbusiness OR entrepreneur software broken OR "not working" help',
    'site:reddit.com webdev OR freelance "client needs" OR project developer',
    # Site-targeted: other social
    'site:linkedin.com "frustrated with" OR broken software OR SaaS post',
    'site:linkedin.com "software problem" OR "integration issue" OR broken post',
    # General complaint queries
    'Facebook group small business software issue OR help',
    'Twitter software broken complaint "need developer" help',
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
