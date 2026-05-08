from .reddit import RedditScraper
from .github_scraper import GitHubScraper
from .hackernews import HackerNewsScraper
from .microsoft import MicrosoftCommunityScraper

ALL_SCRAPERS = [RedditScraper, GitHubScraper, HackerNewsScraper, MicrosoftCommunityScraper]
