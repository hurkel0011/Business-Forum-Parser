from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: official community forum
    'site:community.atlassian.com Jira error OR broken OR "not working" OR help',
    'site:community.atlassian.com Confluence error OR broken OR migration OR help',
    'site:community.atlassian.com Bitbucket pipeline OR error OR broken OR help',
    'site:community.atlassian.com workflow OR plugin OR automation issue OR bug',
    # Site-targeted: Reddit discussions
    'site:reddit.com Jira error OR broken OR "not working" OR help',
    'site:reddit.com Confluence error OR broken OR migration OR help',
    'site:reddit.com Bitbucket pipeline OR error OR broken OR help',
    # Site-targeted: StackOverflow
    'site:stackoverflow.com Jira API error OR broken OR workflow help',
    'site:stackoverflow.com Confluence API error OR plugin OR macro help',
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
            queries = [
                f'site:community.atlassian.com {query}',
                f'site:reddit.com Jira OR Confluence OR Bitbucket {query}',
                f'Jira OR Confluence OR Bitbucket {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Atlassian", limit, url_filter=_label)
