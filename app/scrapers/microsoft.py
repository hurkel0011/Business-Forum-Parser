from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'techcommunity.microsoft.com error OR issue OR "not working" OR broken',
    'techcommunity.microsoft.com integration OR API OR migration OR help',
    'answers.microsoft.com error OR "not working" OR broken OR help software',
    'learn.microsoft.com/answers issue OR error OR help OR deploy',
    'techcommunity.microsoft.com Azure OR "365" OR Teams OR SharePoint problem',
    'techcommunity.microsoft.com PowerShell OR automation OR workflow issue',
]


def _label(url):
    if "techcommunity.microsoft.com" in url:
        return "Microsoft Community"
    if "answers.microsoft.com" in url:
        return "Microsoft Answers"
    if "learn.microsoft.com" in url:
        return "Microsoft Learn"
    return "Microsoft"


class MicrosoftCommunityScraper(BaseScraper):
    """Microsoft community forums — Tech Community, Answers, Learn Q&A."""

    name = "Microsoft Community"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'techcommunity.microsoft.com {query}',
                f'answers.microsoft.com {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Microsoft", limit, url_filter=_label)
