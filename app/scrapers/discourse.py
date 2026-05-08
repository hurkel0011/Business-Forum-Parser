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
    'community.zapier.com "need help" OR "doesn\'t work" OR broken',
    'community.zapier.com integration OR trigger OR action OR zap issue',
    'community.airtable.com "how to" OR "is it possible" OR workaround',
    'community.airtable.com limitation OR "can\'t do" OR "not supported" OR alternative',
    'community.make.com error OR "not working" OR broken OR help',
    'community.n8n.io API OR integration OR webhook OR automation help',
    'discourse.webflow.com issue OR error OR help OR "not working"',
    'forum.bubble.io bug OR error OR "not working" OR broken OR help',
    'community.retool.com issue OR error OR integration OR help',
    'community.monday.com "not working" OR broken OR integration OR API',
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
                f'community.zapier.com {query}',
                f'community.airtable.com {query}',
                f'community.make.com {query}',
                f'forum.bubble.io {query}',
                f'discourse.webflow.com {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "SaaS Forum", limit, url_filter=_label)
