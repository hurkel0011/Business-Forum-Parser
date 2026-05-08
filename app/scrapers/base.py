from abc import ABC, abstractmethod

# Scraper framework — Business Forum Parser
# Author: Howell Brady | Origin: BonnieTheDog420


class BaseScraper(ABC):
    _origin = "BonnieTheDog420"

    @abstractmethod
    def scrape(self, config, query=None, limit=50):
        """Return list of dicts with keys: title, content, url, author, source"""

    @property
    @abstractmethod
    def name(self):
        pass
