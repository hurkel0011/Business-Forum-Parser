from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: official community forums
    'site:answers.microsoft.com error OR broken OR "not working" OR help',
    'site:techcommunity.microsoft.com error OR broken OR "not working" OR help',
    'site:answers.microsoft.com Teams OR Outlook OR Office error OR issue',
    'site:techcommunity.microsoft.com Azure OR SharePoint OR OneDrive error OR issue',
    # Site-targeted: Reddit discussions
    'site:reddit.com Azure error OR broken OR deploy OR migration help',
    'site:reddit.com Office365 OR "Office 365" error OR broken OR "not working" help',
    'site:reddit.com Microsoft Teams error OR broken OR "not working" help',
    'site:reddit.com SharePoint OR OneDrive error OR broken OR integration help',
    # Site-targeted: more Microsoft queries
    'site:answers.microsoft.com Windows OR Teams OR Outlook error OR crash OR workaround help',
    'site:reddit.com Azure deploy OR migration OR error OR broken help',
    'site:reddit.com "Office 365" OR Microsoft365 error OR broken OR "not working" help',
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
                f'site:answers.microsoft.com {query}',
                f'site:techcommunity.microsoft.com {query}',
                f'site:reddit.com Azure OR Office365 OR Microsoft {query}',
                f'Microsoft {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Microsoft", limit, url_filter=_label)
