from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    # Site-targeted: official community forums
    'site:discussions.unity.com error OR crash OR broken OR bug OR help',
    'site:forums.unrealengine.com error OR crash OR broken OR bug OR help',
    'site:forum.godotengine.org error OR crash OR broken OR bug OR help',
    # Site-targeted: Reddit discussions
    'site:reddit.com Unity error OR crash OR broken OR bug help',
    'site:reddit.com "Unreal Engine" error OR crash OR broken OR bug help',
    'site:reddit.com Godot error OR crash OR broken OR bug help',
    'site:reddit.com Blender error OR crash OR broken OR plugin help',
    # Site-targeted: more Reddit and forum queries
    'site:reddit.com Unity plugin OR pipeline OR shader error OR broken help',
    'site:reddit.com "Unreal Engine" build OR pipeline OR packaging error help',
    'site:reddit.com Godot export OR build OR GDScript error OR broken help',
]


def _label(url):
    if "unity.com" in url or "unity3d.com" in url:
        return "Unity"
    if "unrealengine.com" in url:
        return "Unreal Engine"
    if "godotengine.org" in url:
        return "Godot"
    if "itch.io" in url:
        return "itch.io"
    if "blender" in url:
        return "Blender"
    return "GameDev"


class GameDevScraper(BaseScraper):
    """Game dev / Creative tool forums — Unity, Unreal, Godot devs with tooling and pipeline issues."""

    name = "Game Dev / Creative"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:discussions.unity.com {query}',
                f'site:forums.unrealengine.com {query}',
                f'site:forum.godotengine.org {query}',
                f'site:reddit.com Unity OR "Unreal Engine" OR Godot {query}',
                f'Unity OR "Unreal Engine" OR Godot {query} community forum help',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "GameDev", limit, url_filter=_label)
