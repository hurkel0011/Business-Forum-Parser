from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'bbb.org/complaint software OR website OR app OR service',
    'bbb.org customer reviews software OR technology OR web',
    'sitejabber.com/reviews terrible OR broken OR scam OR "doesn\'t work" software',
    'sitejabber.com/reviews "website builder" OR hosting OR saas OR crm',
    'pissedconsumer.com software OR app OR website OR service broken OR terrible',
    'pissedconsumer.com developer OR "tech support" OR integration OR "data loss"',
    'consumeraffairs.com/technology review terrible OR avoid',
    'consumeraffairs.com/computers problem OR issue OR broken OR refund',
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
                f'bbb.org {query}',
                f'sitejabber.com {query}',
                f'pissedconsumer.com {query}',
                f'consumeraffairs.com {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Complaints", limit, url_filter=_label)
