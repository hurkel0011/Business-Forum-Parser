from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'community.airtable.com "not working" OR error OR broken OR help OR limitation',
    'community.airtable.com automation OR integration OR API OR sync issue',
    'community.zapier.com "not working" OR error OR broken OR help',
    'community.zapier.com integration OR trigger OR action OR zap issue',
    'community.make.com error OR "not working" OR broken OR help',
    'forum.bubble.io bug OR error OR "not working" OR broken OR help',
    'forum.bubble.io API OR plugin OR integration issue',
    'reddit.com/r/Notion "not working" OR broken OR API OR integration OR automation',
    '"monday.com" "not working" OR broken OR integration OR automation OR error OR API',
    '"no-code" OR "low-code" limitation OR broken OR "need developer" OR custom OR workaround',
]


def _label(url):
    if "airtable.com" in url:
        return "Airtable"
    if "zapier.com" in url:
        return "Zapier"
    if "make.com" in url or "integromat" in url:
        return "Make"
    if "bubble.io" in url:
        return "Bubble"
    if "notion" in url.lower():
        return "Notion"
    if "monday.com" in url:
        return "Monday.com"
    return "No-Code"


class NoCodePlatformsScraper(BaseScraper):
    """No-code/Low-code platform forums — Airtable, Zapier, Make, Bubble users hitting limitations."""

    name = "No-Code / Low-Code"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'community.airtable.com {query}',
                f'community.zapier.com {query}',
                f'forum.bubble.io {query}',
                f'"no-code" OR "low-code" {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "No-Code", limit, url_filter=_label)
