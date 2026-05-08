from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'digitalocean.com/community help OR error OR "not working" OR broken',
    'digitalocean.com/community migration OR deploy OR SSL OR DNS issue',
    'community.cloudflare.com issue OR error OR "not working" OR blocked',
    'community.cloudflare.com help OR need OR workaround',
    'repost.aws error OR issue OR help OR "not working"',
    'repost.aws migration OR lambda OR S3 OR EC2 problem',
    'answers.netlify.com deploy OR build OR error OR broken OR help',
    'vercel next.js discussions bug OR help OR error OR issue',
]


def _label(url):
    if "digitalocean.com" in url:
        return "DigitalOcean"
    if "cloudflare.com" in url:
        return "Cloudflare"
    if "repost.aws" in url or "aws.amazon" in url:
        return "AWS"
    if "netlify.com" in url:
        return "Netlify"
    if "vercel" in url or "next.js" in url:
        return "Vercel"
    return "Cloud"


class CloudForumsScraper(BaseScraper):
    """Cloud/hosting community forums — DigitalOcean, Cloudflare, AWS, Netlify, Vercel."""

    name = "Cloud Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'digitalocean.com/community {query}',
                f'community.cloudflare.com {query}',
                f'repost.aws {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Cloud", limit, url_filter=_label)
