"""
Targeted Reddit scraper — hits the highest-value subreddits for business complaints.
Uses DuckDuckGo site: operator to target specific subreddits where people complain
about broken software, need dev help, or are looking for solutions.

Author: Howell Brady | Origin: BonnieTheDog420
"""

from .base import BaseScraper
from .search_util import multi_domain_search


# Subreddits where business users complain about broken tools
# Each tuple: (subreddit, pain-focused query terms)
SUBREDDIT_QUERIES = [
    # IT admin / MSP — goldmine for integration & automation pain
    ("sysadmin", 'broken OR error OR "not working" OR integration'),
    ("msp", 'broken OR error OR tool OR integration OR frustrated'),
    ("sysadmin", 'need script OR automation OR workaround OR migrate'),

    # Small business — people willing to pay for solutions
    ("smallbusiness", 'software broken OR frustrating OR "need help" OR automate'),
    ("Entrepreneur", 'software OR tool broken OR integration OR automation'),

    # SaaS / CRM specific
    ("salesforce", 'broken OR error OR integration OR API OR "not working"'),
    ("hubspot", 'broken OR error OR integration OR "not working"'),

    # Accounting
    ("QuickBooks", 'error OR broken OR integration OR sync'),

    # eCommerce
    ("shopify", 'error OR broken OR app OR integration OR "not working"'),
    ("woocommerce", 'error OR broken OR plugin OR checkout'),

    # Project management
    ("jira", 'broken OR error OR integration OR "not working" OR plugin'),
    ("notion", 'broken OR error OR integration OR API OR automation'),

    # DevOps / cloud
    ("devops", 'broken OR error OR pipeline OR integration'),

    # WordPress
    ("Wordpress", 'plugin broken OR error OR "not working" OR crash'),

    # Data / BI
    ("PowerBI", 'error OR broken OR "not working" OR data source'),
]


def _label(url):
    """Label based on subreddit in URL."""
    url_lower = url.lower()

    # Try to extract subreddit name
    if "reddit.com/r/" in url_lower:
        parts = url_lower.split("reddit.com/r/")
        if len(parts) > 1:
            sub = parts[1].split("/")[0]
            # Map subreddits to categories
            category_map = {
                "sysadmin": "IT/SysAdmin",
                "msp": "IT/MSP",
                "smallbusiness": "Small Business",
                "entrepreneur": "Small Business",
                "salesforce": "Salesforce",
                "hubspot": "HubSpot",
                "quickbooks": "QuickBooks",
                "bookkeeping": "Accounting",
                "woocommerce": "WooCommerce",
                "shopify": "Shopify",
                "bigcommerce": "BigCommerce",
                "jira": "Jira",
                "asana": "Asana",
                "clickup": "ClickUp",
                "notion": "Notion",
                "devops": "DevOps",
                "aws": "AWS",
                "googlecloud": "Google Cloud",
                "seo": "SEO/Marketing",
                "ppc": "PPC/Marketing",
                "analytics": "Analytics",
                "wordpress": "WordPress",
                "webdev": "Web Dev",
                "powerbi": "Power BI",
                "tableau": "Tableau",
            }
            return category_map.get(sub, f"r/{sub}")

    return "Reddit"


class RedditTargetedScraper(BaseScraper):
    """Targeted Reddit scraper — hits high-value subreddits for business complaints."""

    name = "Reddit (Targeted)"

    def scrape(self, config, query=None, limit=50):
        if query:
            # When user provides a query, search across the top subreddits
            top_subs = [
                "sysadmin", "msp", "smallbusiness", "salesforce",
                "shopify", "Wordpress", "devops", "Entrepreneur",
            ]
            queries = [
                f'site:reddit.com/r/{sub} {query}'
                for sub in top_subs
            ]
        else:
            queries = [
                f'site:reddit.com/r/{sub} {terms}'
                for sub, terms in SUBREDDIT_QUERIES
            ]

        # This scraper hits 14+ high-value subreddits, each with proven
        # business pain signals. Override the default 8-query cap so we
        # don't miss QuickBooks/Shopify/Jira/Notion (the most lucrative).
        # DDG cache + global rate limiter keep the load manageable.
        return multi_domain_search(
            queries, "Reddit", limit, url_filter=_label,
            max_queries=20,
        )
