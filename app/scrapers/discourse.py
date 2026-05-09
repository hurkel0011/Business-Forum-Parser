from .base import BaseScraper
from .search_util import multi_domain_search

FORUMS = [
    ("community.zapier.com", "Zapier"),
    ("community.airtable.com", "Airtable"),
    ("community.make.com", "Make/Integromat"),
    ("community.n8n.io", "n8n"),
    ("community.notion.so", "Notion"),
    ("discourse.webflow.com", "Webflow"),
    ("forum.bubble.io", "Bubble"),
    ("meta.discourse.org", "Discourse"),
    ("community.retool.com", "Retool"),
    ("community.monday.com", "Monday.com"),
]

QUERIES = [
    # Site-targeted: Discourse meta forum
    'site:meta.discourse.org error OR broken OR bug OR help',
    'site:meta.discourse.org plugin OR theme OR migration OR upgrade issue',
    # Site-targeted: Reddit discussions
    'site:reddit.com Discourse error OR broken OR "not working" OR help',
    'site:reddit.com Discourse plugin OR theme OR migration help',
    # General SaaS community forum queries
    'site:community.notion.so error OR broken OR bug OR help',
    'site:community.monday.com error OR broken OR integration OR help',
    'site:discourse.webflow.com error OR broken OR bug OR help',
    'site:community.retool.com error OR broken OR integration OR help',
    # General complaint queries
    'Discourse community error plugin help',
    'Webflow community error broken help',
]


def _label(url):
    for domain, name in FORUMS:
        if domain in url:
            return name
    return "SaaS Forum"


class DiscourseScraper(BaseScraper):
    """No-code/SaaS community forums (Zapier, Airtable, Make, Notion, etc.) — people hitting platform limits."""

    name = "SaaS Communities"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:meta.discourse.org {query}',
                f'site:community.notion.so {query}',
                f'site:community.monday.com {query}',
                f'site:reddit.com Discourse OR Notion OR Monday.com {query}',
                f'Discourse OR Notion OR Monday.com {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "SaaS Forum", limit, url_filter=_label)
