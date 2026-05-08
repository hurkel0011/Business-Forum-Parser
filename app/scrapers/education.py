from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'community.canvaslms.com "not working" OR error OR broken OR help',
    'community.canvaslms.com integration OR API OR LTI OR sync',
    'moodle.org/mod/forum error OR issue OR broken OR help OR plugin',
    'community.anthology.com issue OR error OR "not working" OR help',
    'support.google.com/edu "not working" OR issue OR error OR broken',
    'community.teachable.com "not working" OR broken OR integration OR bug',
    '"LMS" OR "learning management" broken OR "not working" OR "need help" integration OR API',
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
                f'community.canvaslms.com {query}',
                f'moodle.org/mod/forum {query}',
                f'"LMS" OR "edtech" {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "EdTech", limit, url_filter=_label)
