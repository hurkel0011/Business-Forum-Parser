from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: official community forums
    'site:community.airtable.com error OR broken OR limitation OR help',
    'site:community.zapier.com error OR broken OR "not working" OR help',
    'site:community.make.com error OR broken OR scenario OR help',
    'site:forum.bubble.io error OR broken OR bug OR help',
    # Site-targeted: Reddit discussions
    'site:reddit.com Airtable error OR broken OR limitation OR help',
    'site:reddit.com Zapier error OR broken OR "not working" OR help',
    'site:reddit.com Make automation error OR broken OR help',
    'site:reddit.com Bubble app error OR broken OR bug OR help',
    'site:reddit.com Notion error OR broken OR API OR integration help',
    # General complaint queries
    'Airtable community error workaround help',
    'Zapier community integration error help',
    'Notion community error integration help',
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
                f'site:community.airtable.com {query}',
                f'site:community.zapier.com {query}',
                f'site:community.make.com {query}',
                f'site:forum.bubble.io {query}',
                f'site:reddit.com Airtable OR Zapier OR Make OR Notion {query}',
                f'Airtable OR Zapier OR Notion {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "No-Code", limit, url_filter=_label)
