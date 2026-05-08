from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Facebook groups
    'facebook.com/groups "need developer" OR "looking for someone to build" OR "website help"',
    'facebook.com/groups "fix my website" OR "software issue" OR "need automation"',
    'facebook.com/groups "small business" "need help" software OR website OR app',
    # LinkedIn
    'linkedin.com/posts "frustrated with" OR broken OR "need a developer"',
    'linkedin.com/posts "looking for" developer OR freelancer OR "someone to build"',
    'linkedin.com/pulse "software problem" OR "integration issue" OR automation',
    # Twitter/X
    'twitter.com OR x.com "need developer" OR "hire developer" OR "looking for freelancer"',
    'twitter.com OR x.com "broken software" OR "integration doesn\'t work" OR "urgent fix"',
    # Reddit business subs
    'reddit.com/r/smallbusiness OR reddit.com/r/Entrepreneur "need help" software OR automation',
    'reddit.com/r/webdev OR reddit.com/r/freelance "client needs" OR project OR "looking for"',
    'reddit.com/r/forhire OR reddit.com/r/slavelabour hiring OR "looking for" developer OR automation',
]


def _label(url):
    if "facebook.com" in url:
        return "Facebook"
    if "linkedin.com" in url:
        return "LinkedIn"
    if "twitter.com" in url or "x.com" in url:
        return "Twitter/X"
    if "reddit.com" in url:
        return "Reddit"
    return "Social"


class SocialMediaScraper(BaseScraper):
    """Search Facebook groups, Twitter/X, LinkedIn, and Reddit via Bing."""

    name = "Social Media"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'facebook.com/groups {query}',
                f'linkedin.com/posts {query}',
                f'twitter.com OR x.com {query}',
                f'reddit.com {query} hire OR need OR help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Social", limit, url_filter=_label)
