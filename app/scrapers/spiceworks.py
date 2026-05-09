from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: official community forum
    'site:community.spiceworks.com error OR broken OR help OR issue',
    'site:community.spiceworks.com network OR server OR firewall OR VPN issue help',
    'site:community.spiceworks.com migration OR upgrade OR deploy OR replace help',
    'site:community.spiceworks.com automation OR script OR PowerShell OR GPO help',
    # Site-targeted: Reddit discussions
    'site:reddit.com sysadmin IT software error OR broken OR "not working" help',
    'site:reddit.com sysadmin network OR server OR firewall OR VPN issue help',
    'site:reddit.com sysadmin automation OR script OR migration help',
    # General complaint queries
    'Spiceworks community IT error help',
    'sysadmin community software error workaround help',
]


def _label(url):
    if "spiceworks.com" in url:
        return "Spiceworks"
    return None


class SpiceworksScraper(BaseScraper):
    """Spiceworks IT Community — sysadmins and IT pros with enterprise tool problems."""

    name = "Spiceworks"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:community.spiceworks.com {query}',
                f'site:reddit.com sysadmin IT {query}',
                f'Spiceworks IT {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "Spiceworks", limit, url_filter=_label)
