from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'community.bamboohr.com issue OR "not working" OR integration OR help',
    '"BambooHR" "not working" OR broken OR integration OR API OR bug',
    '"Workday" error OR "not working" OR integration OR broken OR help',
    '"ADP" payroll OR workforce "not working" OR error OR broken OR integration',
    '"Greenhouse" OR "Lever" OR "ATS" integration OR broken OR "not working" OR API OR bug',
    '"HR software" OR "HRIS" OR "payroll software" "not working" OR broken OR "need help" integration',
    '"Gusto" OR "Rippling" "not working" OR error OR broken OR integration OR help',
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
                f'"HR software" OR "HRIS" {query}',
                f'"BambooHR" OR "Workday" OR "ADP" {query}',
                f'"payroll" OR "recruiting" {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "HR Tech", limit, url_filter=_label)
