from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: GitHub discussions
    'site:github.com/discussions bug OR error OR "not working" OR broken help',
    'site:github.com/discussions help OR question OR "how to" integration issue',
    'site:github.com/discussions "feature request" OR workaround OR alternative help',
    'site:github.com/discussions deployment OR production OR performance error help',
    'site:github.com/discussions API OR webhook OR authentication OR plugin issue help',
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
            queries = [
                f'site:github.com/discussions {query} error help',
                f'site:github.com/discussions {query} issue bug',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "GitHub Disc.", limit, url_filter=_label)
