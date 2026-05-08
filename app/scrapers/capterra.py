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

PRODUCTS = [
    ("salesforce", "Salesforce"),
    ("hubspot-crm", "HubSpot"),
    ("jira", "Jira"),
    ("zendesk", "Zendesk"),
    ("monday-com", "Monday.com"),
    ("asana", "Asana"),
    ("quickbooks", "QuickBooks"),
    ("shopify", "Shopify"),
    ("freshdesk", "Freshdesk"),
    ("clickup", "ClickUp"),
    ("zoho-crm", "Zoho CRM"),
    ("pipedrive", "Pipedrive"),
    ("wix", "Wix"),
    ("squarespace", "Squarespace"),
    ("mailchimp", "Mailchimp"),
]


class CapterraScraper(BaseScraper):
    """Capterra software reviews — complaints about business tools."""

    name = "Capterra"

    def scrape(self, config, query=None, limit=50):
        posts = []

        for slug, name in PRODUCTS[:10]:
            if len(posts) >= limit:
                break
            try:
                url = f"https://www.capterra.com/p/{slug}/reviews/"
                resp = requests.get(
                    url,
                    params={"rating": "1-2"},
                    headers=HEADERS,
                    timeout=20,
                )
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                for review in soup.select('[class*="review"]'):
                    title_el = review.select_one("h3, [class*='title']")
                    cons_el = review.select_one(
                        "[class*='cons'], [class*='dislike'], [class*='negative']"
                    )
                    body_el = review.select_one("[class*='body'], [class*='text'], p")

                    content = ""
                    if cons_el:
                        content = "Cons: " + cons_el.get_text(strip=True)
                    elif body_el:
                        content = body_el.get_text(strip=True)

                    if not content or len(content) < 30:
                        continue

                    posts.append({
                        "source": f"Capterra/{name}",
                        "title": (
                            title_el.get_text(strip=True) if title_el
                            else f"{name} review complaint"
                        ),
                        "content": content[:2000],
                        "url": url,
                        "author": "reviewer",
                    })

            except Exception:
                continue

        return posts[:limit]
