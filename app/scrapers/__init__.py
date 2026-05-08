from .google_search import DuckDuckGoScraper
from .github_scraper import GitHubScraper
from .hackernews import HackerNewsScraper
from .microsoft import MicrosoftCommunityScraper
from .stackoverflow import StackOverflowScraper
from .trustpilot import TrustpilotScraper
from .g2_reviews import G2ReviewScraper
from .indiehackers import IndieHackersScraper
from .enricher import enrich_post

ALL_SCRAPERS = [
    DuckDuckGoScraper,
    GitHubScraper,
    HackerNewsScraper,
    MicrosoftCommunityScraper,
    StackOverflowScraper,
    TrustpilotScraper,
    G2ReviewScraper,
    IndieHackersScraper,
]
