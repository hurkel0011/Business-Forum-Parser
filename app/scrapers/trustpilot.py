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

# B2B software categories on Trustpilot
CATEGORIES = [
    "business_software",
    "web_hosting_and_domain",
    "telecommunications_provider",
    "it_services_and_it_consulting",
]

# Popular B2B companies people complain about
COMPANIES = [
    "salesforce.com", "hubspot.com", "zendesk.com",
    "atlassian.com", "freshworks.com", "monday.com",
    "asana.com", "clickup.com", "notion.so",
    "quickbooks.intuit.com", "xero.com",
    "godaddy.com", "squarespace.com", "wix.com",
    "shopify.com", "bigcommerce.com",
    "mailchimp.com", "sendgrid.com",
    "twilio.com", "stripe.com",
]


class TrustpilotScraper(BaseScraper):
    name = "Trustpilot"

    def scrape(self, config, query=None, limit=50):
        posts = []

        # Scrape low-star reviews for specific B2B companies
        for company in COMPANIES[:10]:
            if len(posts) >= limit:
                break
            try:
                url = f"https://www.trustpilot.com/review/{company}"
                resp = requests.get(
                    url,
                    params={"stars": "1", "stars": "2"},
                    headers=HEADERS,
                    timeout=20,
                )
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                for review in soup.select('[data-service-review-card-paper]'):
                    title_el = review.select_one('[data-service-review-title-typography]')
                    body_el = review.select_one('[data-service-review-text-typography]')
                    rating_el = review.select_one('[data-service-review-rating]')

                    if not title_el:
                        continue

                    # Only grab 1-2 star reviews (complaints)
                    rating_text = rating_el.get("data-service-review-rating", "5") if rating_el else "5"
                    try:
                        rating = int(rating_text)
                    except (ValueError, TypeError):
                        rating = 5

                    if rating > 2:
                        continue

                    body = body_el.get_text(strip=True) if body_el else ""

                    posts.append({
                        "source": f"Trustpilot/{company.split('.')[0]}",
                        "title": title_el.get_text(strip=True),
                        "content": body[:2000],
                        "url": url,
                        "author": "unknown",
                    })

            except Exception:
                continue

        return posts[:limit]
