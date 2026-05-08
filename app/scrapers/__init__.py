from .google_search import DuckDuckGoScraper
from .github_scraper import GitHubScraper
from .hackernews import HackerNewsScraper
from .microsoft import MicrosoftCommunityScraper
from .stackoverflow import StackOverflowScraper
from .enricher import enrich_post

ALL_SCRAPERS = [
    DuckDuckGoScraper,
    GitHubScraper,
    HackerNewsScraper,
    MicrosoftCommunityScraper,
    StackOverflowScraper,
]
