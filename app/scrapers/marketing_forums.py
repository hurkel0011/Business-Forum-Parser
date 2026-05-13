from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Highest-value first — these were being dropped by the 8-query cap
    # Email marketing platforms (small business, recurring pain)
    'site:reddit.com Mailchimp error OR broken OR "not working" OR deliverability help',
    'site:reddit.com ActiveCampaign error OR broken OR "not working" OR help',
    'site:reddit.com Klaviyo error OR broken OR "not working" OR integration help',
    # Google Analytics / GA4 — universal pain, every business runs into it
    'site:reddit.com "Google Analytics" OR GA4 broken OR error OR migration OR "not working"',
    # Google Tag Manager — integration pain on top of GA
    'site:reddit.com "Google Tag Manager" OR GTM error OR broken OR tracking',
    # SEO tools — agencies with budgets
    'site:reddit.com SEMrush OR Ahrefs error OR broken OR "not working" help',
    'site:reddit.com Moz SEO error OR broken OR "not working" help',
    # Integration / automation variants (catch what the above miss)
    'site:reddit.com Klaviyo integration OR sync OR "not working" error help',
    # Demoted (lower priority — variants of above)
    'site:reddit.com Mailchimp automation OR deliverability OR sync error help',
    'site:reddit.com ActiveCampaign integration OR automation OR sync error help',
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
