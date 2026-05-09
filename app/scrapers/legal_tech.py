from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Reddit discussions
    'site:reddit.com Clio "legal software" error OR broken OR integration help',
    'site:reddit.com PracticePanther error OR broken OR "not working" help',
    'site:reddit.com MyCase error OR broken OR "not working" help',
    'site:reddit.com LawPay error OR broken OR billing OR integration help',
    'site:reddit.com "legal tech" OR "practice management" software error OR broken help',
    # General complaint queries
    'Clio community error integration help',
    'PracticePanther community error billing help',
    'MyCase community error sync help',
    '"legal software" community error workaround help',
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
                f'site:reddit.com Clio OR "legal software" {query}',
                f'site:reddit.com PracticePanther OR MyCase OR LawPay {query}',
                f'Clio OR "legal software" {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Legal Tech", limit, url_filter=_label)
