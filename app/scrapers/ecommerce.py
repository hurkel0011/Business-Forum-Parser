import requests
import time
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .base import BaseScraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}

# eCommerce platform communities beyond Shopify
QUERIES = [
    # BigCommerce
    'site:support.bigcommerce.com OR site:community.bigcommerce.com "help" OR "issue" OR "broken" OR "error"',
    # WooCommerce (separate from WordPress general)
    'site:wordpress.org/support/plugin/woocommerce "not working" OR "broken" OR "error" OR "help"',
    'site:wordpress.org/support/plugin/woocommerce "payment" OR "checkout" OR "shipping" issue',
    # Magento / Adobe Commerce
    'site:community.magento.com "issue" OR "error" OR "help" OR "broken" OR "fix"',
    # PrestaShop
    'site:prestashop.com/forums "help" OR "error" OR "broken" OR "issue" OR "bug"',
    # Squarespace
    'site:forum.squarespace.com "not working" OR "broken" OR "help" OR "custom code"',
    'site:forum.squarespace.com "developer" OR "CSS" OR "JavaScript" OR "integration"',
    # Wix
    'site:community.wix.com "help" OR "broken" OR "issue" OR "not working" OR "bug"',
]


class EcommerceScraper(BaseScraper):
    """eCommerce platform forums — BigCommerce, WooCommerce, Magento, Squarespace, Wix."""

    name = "eCommerce Forums"

    def scrape(self, config, query=None, limit=50):
        if query:
            queries = [
                f'site:community.bigcommerce.com "{query}"',
                f'site:wordpress.org/support/plugin/woocommerce "{query}"',
                f'site:community.magento.com "{query}"',
                f'site:forum.squarespace.com "{query}"',
                f'site:community.wix.com "{query}"',
            ]
        else:
            queries = QUERIES

        all_posts = []
        per_query = max(5, limit // len(queries))

        for q in queries:
            try:
                url = f"https://www.bing.com/search?q={quote_plus(q)}&count={per_query}"
                resp = requests.get(url, headers=HEADERS, timeout=20)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                for result in soup.select("#b_results .b_algo"):
                    title_el = result.select_one("h2 a")
                    snippet_el = result.select_one(".b_caption p")

                    if not title_el:
                        continue

                    href = title_el.get("href", "")
                    if not href.startswith("http"):
                        continue

                    source = "eCommerce"
                    if "bigcommerce.com" in href:
                        source = "BigCommerce"
                    elif "woocommerce" in href:
                        source = "WooCommerce"
                    elif "magento.com" in href:
                        source = "Magento"
                    elif "squarespace.com" in href:
                        source = "Squarespace"
                    elif "prestashop.com" in href:
                        source = "PrestaShop"
                    elif "wix.com" in href:
                        source = "Wix"

                    all_posts.append({
                        "source": source,
                        "title": title_el.get_text(strip=True),
                        "content": snippet_el.get_text(strip=True) if snippet_el else "",
                        "url": href,
                        "author": "unknown",
                    })

                time.sleep(0.5)
            except Exception:
                continue

        seen = set()
        unique = []
        for p in all_posts:
            if p["url"] not in seen:
                seen.add(p["url"])
                unique.append(p)

        return unique[:limit]
