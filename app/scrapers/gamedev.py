from .base import BaseScraper
from .search_util import multi_domain_search

QUERIES = [
    'forum.unity.com bug OR error OR "not working" OR broken OR help',
    'forum.unity.com integration OR plugin OR asset OR pipeline issue',
    'forums.unrealengine.com bug OR error OR "not working" OR crash OR help',
    'forum.godotengine.org bug OR error OR "not working" OR help OR issue',
    'reddit.com/r/gamedev tool OR pipeline OR plugin broken OR "not working" OR need OR help',
    '"Blender" OR "Adobe" plugin OR integration OR automation broken OR "not working" OR error',
    'itch.io/community bug OR error OR "not working" OR broken OR help tool OR plugin',
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
                f'forum.unity.com {query}',
                f'forums.unrealengine.com {query}',
                f'"game dev" OR "game development" {query}',
            ]
        else:
            queries = QUERIES
        return multi_domain_search(queries, "GameDev", limit, url_filter=_label)
