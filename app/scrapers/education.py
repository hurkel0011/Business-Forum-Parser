from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: official community forums
    'site:community.canvaslms.com error OR broken OR integration OR help',
    'site:community.blackboard.com error OR broken OR integration OR help',
    'site:moodle.org/mod/forum error OR broken OR plugin OR help',
    # Site-targeted: Reddit discussions
    'site:reddit.com "Canvas LMS" error OR broken OR "not working" OR help',
    'site:reddit.com Blackboard error OR broken OR "not working" OR help',
    'site:reddit.com Moodle error OR broken OR plugin OR help',
    'site:reddit.com "Google Classroom" error OR broken OR integration help',
    # Site-targeted: more Reddit education queries
    'site:reddit.com "Canvas LMS" broken OR integration OR sync error help',
    'site:reddit.com Moodle plugin OR upgrade OR migration error help',
    'site:reddit.com Blackboard integration OR sync OR "not working" error help',
]


def _label(url):
    if "canvaslms.com" in url:
        return "Canvas LMS"
    if "moodle.org" in url:
        return "Moodle"
    if "anthology.com" in url or "blackboard" in url:
        return "Blackboard"
    if "teachable.com" in url:
        return "Teachable"
    if "thinkific" in url:
        return "Thinkific"
    return "EdTech"


class EducationScraper(BaseScraper):
    """EdTech/LMS forums — Canvas, Moodle, Blackboard, course platform users with integration issues."""

    name = "Education / LMS"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:community.canvaslms.com {query}',
                f'site:community.blackboard.com {query}',
                f'site:moodle.org/mod/forum {query}',
                f'site:reddit.com "Canvas LMS" OR Moodle OR Blackboard {query}',
                f'"Canvas LMS" OR Moodle OR Blackboard {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "EdTech", limit, url_filter=_label)
