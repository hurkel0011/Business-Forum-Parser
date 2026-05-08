from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'github.com discussions help OR question OR "how to" integration OR migration',
    'github.com discussions bug OR error OR broken OR "not working"',
    'github.com discussions "feature request" OR need OR workaround OR alternative',
    'github.com discussions deployment OR production OR performance issue',
    'github.com discussions API OR webhook OR authentication OR plugin help',
]


def _label(url):
    if "github.com" in url and "/discussions" in url:
        return "GitHub Disc."
    if "github.com" in url:
        return "GitHub"
    return None


class GitHubDiscussionsScraper(BaseScraper):
    """GitHub Discussions — community Q&A threads across popular repos."""

    name = "GitHub Discussions"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [f'github.com discussions {query}']
        else:
            queries = QUERIES
        return multi_domain_search(queries, "GitHub Disc.", limit, url_filter=_label)
