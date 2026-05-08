from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'community.atlassian.com Jira "not working" OR broken OR error OR bug',
    'community.atlassian.com Confluence help OR issue OR fix OR migrate',
    'community.atlassian.com integration OR API OR webhook OR automation',
    'community.atlassian.com workflow OR "custom field" OR plugin OR marketplace',
    'community.atlassian.com Bitbucket OR pipeline error OR broken OR "doesn\'t work"',
    'community.atlassian.com "need help" OR urgent OR "anyone know how"',
]


def _label(url):
    if "atlassian.com" in url:
        return "Atlassian"
    return None


class AtlassianScraper(BaseScraper):
    """Atlassian Community — Jira, Confluence, Bitbucket users with dev tool problems."""

    name = "Atlassian"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'community.atlassian.com {query}']
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Atlassian", limit, url_filter=_label)
