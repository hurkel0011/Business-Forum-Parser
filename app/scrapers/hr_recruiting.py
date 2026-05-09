from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: official community forums
    'site:community.workday.com error OR broken OR integration OR help',
    # Site-targeted: Reddit discussions
    'site:reddit.com Workday error OR broken OR "not working" OR integration help',
    'site:reddit.com BambooHR error OR broken OR "not working" OR integration help',
    'site:reddit.com ADP payroll error OR broken OR "not working" OR sync help',
    'site:reddit.com Greenhouse ATS error OR broken OR integration help',
    # General complaint queries
    'Workday community error integration help',
    'BambooHR community error sync help',
    'ADP payroll community error integration help',
    'Greenhouse ATS community error help',
]


def _label(url):
    if "bamboohr" in url:
        return "BambooHR"
    if "workday" in url:
        return "Workday"
    if "adp.com" in url:
        return "ADP"
    if "greenhouse" in url:
        return "Greenhouse"
    if "lever.co" in url:
        return "Lever"
    if "gusto.com" in url:
        return "Gusto"
    if "rippling.com" in url:
        return "Rippling"
    return "HR Tech"


class HRRecruitingScraper(BaseScraper):
    """HR/Recruiting platform forums — BambooHR, Workday, ADP users with integration and automation needs."""

    name = "HR / Recruiting"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:community.workday.com {query}',
                f'site:reddit.com Workday OR BambooHR OR ADP {query}',
                f'Workday OR BambooHR OR ADP OR Greenhouse {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "HR Tech", limit, url_filter=_label)
