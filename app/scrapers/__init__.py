from .google_search import GoogleSearchScraper
from .github_scraper import GitHubScraper
from .hackernews import HackerNewsScraper
from .microsoft import MicrosoftCommunityScraper

ALL_SCRAPERS = [GoogleSearchScraper, GitHubScraper, HackerNewsScraper, MicrosoftCommunityScraper]
