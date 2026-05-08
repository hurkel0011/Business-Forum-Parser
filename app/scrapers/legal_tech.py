from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'community.clio.com issue OR "not working" OR error OR integration OR help',
    '"Clio" law OR legal "not working" OR broken OR integration OR bug',
    '"MyCase" OR "PracticePanther" "not working" OR broken OR error OR integration',
    '"legal software" OR "practice management" "not working" OR broken OR "need help" integration',
    '"contract management" OR "document automation" broken OR "not working" OR error OR need',
    '"legal billing" OR "time tracking" "law firm" "not working" OR broken OR error OR integration',
    '"legal tech" OR "lawtech" issue OR problem OR "not working" OR integration',
]


def _label(url):
    if "clio.com" in url:
        return "Clio"
    if "mycase" in url:
        return "MyCase"
    if "practicepanther" in url:
        return "PracticePanther"
    return "Legal Tech"


class LegalTechScraper(BaseScraper):
    """Legal tech forums — Clio, practice management tools, law firms with software issues."""

    name = "Legal Tech"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'"legal software" OR "law firm" {query}',
                f'community.clio.com {query}',
                f'"legal tech" {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Legal Tech", limit, url_filter=_label)
