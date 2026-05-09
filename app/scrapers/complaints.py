from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Reddit discussions
    'site:reddit.com software broken frustrated help',
    'site:reddit.com integration broken paying for fix',
    'site:reddit.com SaaS broken "not working" frustrated help',
    'site:reddit.com software terrible "need developer" fix help',
    # Site-targeted: complaint sites
    'site:bbb.org software OR SaaS OR app broken OR complaint OR "not working"',
    'site:sitejabber.com software OR SaaS broken OR terrible OR "doesn\'t work"',
    'site:pissedconsumer.com software OR app OR service broken OR terrible',
    'site:consumeraffairs.com software OR technology broken OR "not working" OR issue',
    # General complaint queries
    'BBB software complaint broken help',
    'consumer complaint software broken terrible review',
]


def _label(url):
    if "bbb.org" in url:
        return "BBB"
    if "sitejabber.com" in url:
        return "Sitejabber"
    if "pissedconsumer.com" in url:
        return "PissedConsumer"
    if "consumeraffairs.com" in url:
        return "ConsumerAffairs"
    return "Complaints"


class ComplaintsScraper(BaseScraper):
    """Consumer complaint sites — BBB, Sitejabber, PissedConsumer, ConsumerAffairs."""

    name = "Complaint Sites"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:reddit.com {query} software broken frustrated help',
                f'site:bbb.org {query} complaint',
                f'site:sitejabber.com {query} review complaint',
                f'site:pissedconsumer.com {query} complaint',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Complaints", limit, url_filter=_label)
