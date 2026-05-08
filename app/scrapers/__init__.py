from .google_search import DuckDuckGoScraper
from .bing import BingSearchScraper
from .google import GoogleSearchScraper
from .brave import BraveSearchScraper
from .github_scraper import GitHubScraper
from .hackernews import HackerNewsScraper
from .microsoft import MicrosoftCommunityScraper
from .stackoverflow import StackOverflowScraper
from .trustpilot import TrustpilotScraper
from .g2_reviews import G2ReviewScraper
from .indiehackers import IndieHackersScraper
from .upwork import UpworkScraper
from .craigslist import CraigslistScraper
from .social_search import SocialMediaScraper
from .capterra import CapterraScraper
from .quora import QuoraScraper
from .producthunt import ProductHuntScraper
from .wordpress import WordPressScraper
from .shopify import ShopifyScraper
from .devto import DevToScraper
from .freelancer import FreelancerScraper
from .spiceworks import SpiceworksScraper
from .discourse import DiscourseScraper
from .atlassian import AtlassianScraper
from .apple import AppleScraper
from .cloud_forums import CloudForumsScraper
from .complaints import ComplaintsScraper
from .more_freelance import MoreFreelanceScraper
from .saas_vendors import SaaSVendorScraper
from .marketing_forums import MarketingForumsScraper
from .ecommerce import EcommerceScraper
from .github_discussions import GitHubDiscussionsScraper
from .accounting import AccountingScraper
from .enricher import enrich_post

ALL_SCRAPERS = [
    # Search engines
    DuckDuckGoScraper,
    BingSearchScraper,
    GoogleSearchScraper,
    BraveSearchScraper,
    # Developer / tech forums
    GitHubScraper,
    GitHubDiscussionsScraper,
    HackerNewsScraper,
    MicrosoftCommunityScraper,
    StackOverflowScraper,
    AtlassianScraper,
    # Review / complaint sites
    TrustpilotScraper,
    G2ReviewScraper,
    CapterraScraper,
    ComplaintsScraper,
    # Community / Q&A
    IndieHackersScraper,
    QuoraScraper,
    ProductHuntScraper,
    DevToScraper,
    # CMS / eCommerce
    WordPressScraper,
    ShopifyScraper,
    EcommerceScraper,
    # SaaS / No-code / vendor communities
    DiscourseScraper,
    SpiceworksScraper,
    AppleScraper,
    SaaSVendorScraper,
    # Cloud / hosting
    CloudForumsScraper,
    # Accounting / finance
    AccountingScraper,
    # Marketing / SEO
    MarketingForumsScraper,
    # Freelance / gigs
    UpworkScraper,
    CraigslistScraper,
    FreelancerScraper,
    MoreFreelanceScraper,
    # Social media search
    SocialMediaScraper,
]
