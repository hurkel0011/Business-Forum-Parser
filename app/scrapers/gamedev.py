import requests
import time
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .base import BaseScraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}

# Game dev / Creative tools — studios and indie devs with tooling and pipeline issues
QUERIES = [
    # Unity
    'site:forum.unity.com "bug" OR "error" OR "not working" OR "broken" OR "help"',
    'site:forum.unity.com "integration" OR "plugin" OR "asset" OR "pipeline" issue',
    # Unreal Engine
    'site:forums.unrealengine.com "bug" OR "error" OR "not working" OR "crash" OR "help"',
    # Godot
    'site:forum.godotengine.org "bug" OR "error" OR "not working" OR "help" OR "issue"',
    # Game dev tools
    '"game development" "tool" OR "pipeline" OR "plugin" "broken" OR "not working" OR "need" OR "help" site:reddit.com/r/gamedev',
    # Creative tools (Blender, Adobe)
    '"Blender" OR "Adobe" "plugin" OR "integration" OR "automation" "broken" OR "not working" OR "error" OR "help"',
    # Indie dev platforms
    'site:itch.io/community "bug" OR "error" OR "not working" OR "broken" OR "help" tool OR plugin',
]


class GameDevScraper(BaseScraper):
    """Game dev / Creative tool forums — Unity, Unreal, Godot devs with tooling and pipeline issues."""

    name = "Game Dev / Creative"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:forum.unity.com "{query}"',
                f'site:forums.unrealengine.com "{query}"',
                f'"game dev" OR "game development" "{query}"',
            ]
        else:
            queries = QUERIES

        all_posts = []
        per_query = max(5, limit // len(queries))

        for q in queries:
            try:
                url = f"https://www.bing.com/search?q={quote_plus(q)}&count={per_query}"
                resp = requests.get(url, headers=HEADERS, timeout=20)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                for result in soup.select("#b_results .b_algo"):
                    title_el = result.select_one("h2 a")
                    snippet_el = result.select_one(".b_caption p")

                    if not title_el:
                        continue

                    href = title_el.get("href", "")
                    if not href.startswith("http"):
                        continue

                    source = "GameDev"
                    if "unity.com" in href or "unity3d.com" in href:
                        source = "Unity"
                    elif "unrealengine.com" in href:
                        source = "Unreal Engine"
                    elif "godotengine.org" in href:
                        source = "Godot"
                    elif "itch.io" in href:
                        source = "itch.io"
                    elif "blender" in href:
                        source = "Blender"

                    all_posts.append({
                        "source": source,
                        "title": title_el.get_text(strip=True),
                        "content": snippet_el.get_text(strip=True) if snippet_el else "",
                        "url": href,
                        "author": "unknown",
                    })

                time.sleep(0.5)
            except Exception:
                continue

        seen = set()
        unique = []
        for p in all_posts:
            if p["url"] not in seen:
                seen.add(p["url"])
                unique.append(p)

        return unique[:limit]
