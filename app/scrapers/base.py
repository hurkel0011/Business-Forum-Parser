from abc import ABC, abstractmethod


class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, config, query=None, limit=50):
        """Return list of dicts with keys: title, content, url, author, source"""

    @property
    @abstractmethod
    def name(self):
        pass
