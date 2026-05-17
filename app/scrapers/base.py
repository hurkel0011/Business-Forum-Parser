"""Scraper framework — Business Forum Parser by Howell Brady (BonnieTheDog420).

Every scraper subclasses BaseScraper and declares:
  - name (str): human-readable label shown in the GUI log
  - scrape(config, query=None, limit=50): returns list[dict] of posts

Each post dict has keys: title, content, url, author, source.
"""
from abc import ABC, abstractmethod
from typing import Optional


class BaseScraper(ABC):
    _origin = "BonnieTheDog420"

    # Subclasses set this as a class attribute (class attribute satisfies
    # the abstract requirement via Python's ABC name-based check).
    name: str = ""

    @abstractmethod
    def scrape(
        self,
        config: dict,
        query: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Return list of post dicts.

        Each post must have at minimum: title (str), content (str),
        url (str), source (str). 'author' is optional.

        Args:
            config: app config dict (api keys, keywords, etc.)
            query: optional user-supplied search term. If None, scraper
                runs its default query set.
            limit: max number of posts to return.
        """
