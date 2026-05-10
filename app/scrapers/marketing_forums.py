from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: Reddit discussions
    'site:reddit.com Mailchimp error OR broken OR "not working" OR deliverability help',
    'site:reddit.com ActiveCampaign error OR broken OR "not working" OR help',
    'site:reddit.com Klaviyo error OR broken OR "not working" OR integration help',
    'site:reddit.com SEMrush OR Ahrefs error OR broken OR "not working" help',
    'site:reddit.com Moz SEO error OR broken OR "not working" help',
    # Site-targeted: more Reddit marketing queries
    'site:reddit.com Mailchimp automation OR deliverability OR sync error help',
    'site:reddit.com ActiveCampaign integration OR automation OR sync error help',
    'site:reddit.com Klaviyo integration OR sync OR "not working" error help',
    'site:reddit.com Moz OR SEMrush SEO crawl OR audit OR rank error help',
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
                f'site:reddit.com Mailchimp OR ActiveCampaign OR Klaviyo {query}',
                f'site:reddit.com Moz OR SEMrush OR Ahrefs {query}',
                f'Mailchimp OR ActiveCampaign OR Klaviyo {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Marketing", limit, url_filter=_label)
