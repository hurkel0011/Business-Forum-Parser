import requests
from bs4 import BeautifulSoup
from .base import BaseScraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}

# Popular B2B software on G2 that people complain about
PRODUCTS = [
    ("salesforce-crm", "Salesforce"),
    ("hubspot-marketing-hub", "HubSpot"),
    ("jira", "Jira"),
    ("zendesk", "Zendesk"),
    ("slack", "Slack"),
    ("monday-com", "Monday.com"),
    ("asana", "Asana"),
    ("quickbooks-online", "QuickBooks"),
    ("shopify", "Shopify"),
    ("mailchimp-all-in-one-marketing-platform", "Mailchimp"),
    ("clickup", "ClickUp"),
    ("notion", "Notion"),
    ("freshdesk", "Freshdesk"),
    ("intercom", "Intercom"),
    ("pipedrive", "Pipedrive"),
]


class G2ReviewScraper(BaseScraper):
    name = "G2 Reviews"

    def scrape(self, config, query=None, limit=50):
        posts = []

        for slug, name in PRODUCTS[:8]:
            if len(posts) >= limit:
                break
            try:
                # G2 low-star reviews page
                url = f"https://www.g2.com/products/{slug}/reviews"
                resp = requests.get(
                    url,
                    params={"utf8": "✓", "filters[nps_score]": "1,2,3"},
                    headers=HEADERS,
                    timeout=20,
                )
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                for review in soup.select('[itemprop="review"]'):
                    title_el = review.select_one("h3, .review-title")
                    dislike_el = review.select_one(
                        '[data-testid="dislike"], .review-dislike'
                    )
                    problems_el = review.select_one(
                        '[data-testid="problems"], .review-problems'
                    )

                    # Get the "What do you dislike?" section
                    content_parts = []
                    if dislike_el:
                        content_parts.append(
                            "Dislikes: " + dislike_el.get_text(strip=True)
                        )
                    if problems_el:
                        content_parts.append(
                            "Problems: " + problems_el.get_text(strip=True)
                        )

                    # Fallback to full review text
                    if not content_parts:
                        body = review.get_text(strip=True)[:1000]
                        if body:
                            content_parts.append(body)

                    if not content_parts:
                        continue

                    posts.append({
                        "source": f"G2/{name}",
                        "title": (
                            title_el.get_text(strip=True) if title_el
                            else f"{name} complaint"
                        ),
                        "content": " | ".join(content_parts)[:2000],
                        "url": url,
                        "author": "unknown",
                    })

            except Exception:
                continue

        return posts[:limit]
