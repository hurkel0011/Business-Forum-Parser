from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'warriorforum.com "need help" OR "looking for" developer OR programmer OR coder',
    'warriorforum.com fix OR build OR automate website OR software OR tool',
    'growthhackers.com problem OR issue OR help OR "looking for" tool OR software',
    'moz.com/community help OR issue OR broken OR fix SEO OR website',
    'sitepoint.com/community help OR error OR "not working" OR "how to fix"',
    'webmasterworld.com issue OR problem OR broken OR "need help" website',
    'forums.digitalpoint.com "need developer" OR hire OR fix OR build',
    'ecommercefuel.com problem OR issue OR help OR "looking for" developer',
]


def _label(url):
    if "warriorforum.com" in url:
        return "WarriorForum"
    if "growthhackers.com" in url:
        return "GrowthHackers"
    if "moz.com" in url:
        return "Moz"
    if "sitepoint.com" in url:
        return "SitePoint"
    if "webmasterworld.com" in url:
        return "WebmasterWorld"
    if "digitalpoint.com" in url:
        return "DigitalPoint"
    return "Marketing"


class MarketingForumsScraper(BaseScraper):
    """SEO/marketing/webmaster forums — Warrior Forum, Moz, SitePoint, GrowthHackers."""

    name = "Marketing Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'warriorforum.com {query}',
                f'growthhackers.com {query}',
                f'moz.com/community {query}',
                f'sitepoint.com/community {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Marketing", limit, url_filter=_label)
