from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: official community forums
    'site:community.digitalocean.com error OR broken OR help OR issue',
    'site:community.cloudflare.com error OR broken OR help OR issue',
    'site:repost.aws.amazon.com error OR broken OR help OR issue',
    # Site-targeted: Reddit discussions
    'site:reddit.com DigitalOcean error OR broken OR "not working" OR help',
    'site:reddit.com Cloudflare error OR broken OR "not working" OR help',
    'site:reddit.com AWS error OR broken OR migration OR deploy help',
    'site:reddit.com Netlify deploy OR build OR error OR broken help',
    'site:reddit.com Vercel error OR broken OR deploy OR "not working" help',
    # StackOverflow
    'site:stackoverflow.com DigitalOcean deploy error',
    'site:stackoverflow.com Cloudflare error fix',
    'site:stackoverflow.com AWS lambda S3 error',
]


def _label(url):
    if "digitalocean.com" in url:
        return "DigitalOcean"
    if "cloudflare.com" in url:
        return "Cloudflare"
    if "repost.aws" in url or "aws.amazon" in url or "aws" in url:
        return "AWS"
    if "netlify.com" in url:
        return "Netlify"
    if "vercel" in url or "next.js" in url or "nextjs" in url:
        return "Vercel"
    return "Cloud"


class CloudForumsScraper(BaseScraper):
    """Cloud/hosting community forums — DigitalOcean, Cloudflare, AWS, Netlify, Vercel."""

    name = "Cloud Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:community.digitalocean.com {query}',
                f'site:community.cloudflare.com {query}',
                f'site:repost.aws.amazon.com {query}',
                f'site:reddit.com DigitalOcean OR Cloudflare OR AWS OR Netlify OR Vercel {query}',
                f'DigitalOcean OR Cloudflare OR AWS {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Cloud", limit, url_filter=_label)
