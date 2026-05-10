"""
Content enricher — fetches full page content for posts with short snippets.
Gives the classifier more text to work with for better lead scoring.

Author: Howell Brady | Origin: BonnieTheDog420
"""

import requests
import random
from bs4 import BeautifulSoup

USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
]

# CSS selectors ordered by specificity — most specific first
# Each tuple: (selector, description)
CONTENT_SELECTORS = [
    # Reddit
    ("div[data-test-id='post-content']", "Reddit new"),
    (".expando .usertext-body", "Reddit old"),
    (".Post .RichTextJSON-root", "Reddit redesign"),
    # Community forums (Discourse, Lithium, Khoros, Vanilla)
    (".lia-message-body-content", "Lithium/Khoros forum"),
    (".lia-message-body", "Lithium forum fallback"),
    (".post_body", "Discourse post"),
    (".cooked", "Discourse cooked"),
    (".topic-body .regular", "Discourse topic"),
    (".MessageBody", "Vanilla forum"),
    # Stack Overflow / Stack Exchange
    (".s-prose", "Stack Overflow"),
    (".question .postcell .post-text", "SO question"),
    (".answer .post-text", "SO answer"),
    # Salesforce / Trailblazer
    (".cuf-feedBodyText", "Salesforce community"),
    (".slds-rich-text-editor__output", "Salesforce rich text"),
    # HubSpot community
    (".lia-quilt-column-main-content", "HubSpot community"),
    # Cloudflare community
    (".post .cooked", "Cloudflare community"),
    # GitHub
    (".comment-body", "GitHub issue/discussion"),
    (".markdown-body", "GitHub markdown"),
    # General content selectors
    ("article", "article tag"),
    ('[role="main"]', "main role"),
    (".post-content", "post-content class"),
    (".entry-content", "entry-content class"),
    (".question-body", "question-body class"),
    (".message-body", "message-body class"),
    ("#content", "content id"),
    (".content", "content class"),
    ("main", "main tag"),
]


def _get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }


def _extract_text(soup):
    """Extract the best content text from a page using prioritized selectors."""
    # Remove noise elements
    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "noscript", "iframe", "svg"]):
        tag.decompose()

    # Try each selector in priority order
    for selector, _desc in CONTENT_SELECTORS:
        elements = soup.select(selector)
        if elements:
            # Combine text from all matching elements (e.g. multiple comments)
            texts = []
            for el in elements[:5]:  # Cap at 5 elements
                text = el.get_text(separator="\n", strip=True)
                if len(text) > 50:
                    texts.append(text)
            if texts:
                return "\n\n".join(texts)

    # Final fallback: body text
    if soup.body:
        return soup.body.get_text(separator="\n", strip=True)

    return ""


# URL patterns that indicate category/index pages (not individual posts)
_INDEX_PAGE_PATTERNS = [
    "/bd-p/",          # Lithium/Khoros board pages
    "/ct-p/",          # Lithium category pages
    "/categories",     # Forum category listings
    "/forums/",        # Forum index (not specific post)
    "/tags/",          # Tag listings
    "/page/",          # Pagination pages
]


def enrich_post(post):
    """Fetch full page content for a post to give the classifier more text.

    Only fetches if existing content is short (< 500 chars).
    Extracts main content using community-forum-specific CSS selectors.
    Skips known category/index pages that aren't individual complaints.
    """
    url = post.get("url", "")
    existing_content = post.get("content", "")

    # Skip if we already have enough content or no URL
    if not url or len(existing_content) > 500:
        return post

    # Skip category/index pages — they contain many posts, not one complaint
    url_lower = url.lower()
    if any(p in url_lower for p in _INDEX_PAGE_PATTERNS):
        return post

    try:
        resp = requests.get(
            url, headers=_get_headers(), timeout=15,
            allow_redirects=True,
        )
        if resp.status_code != 200:
            return post

        # Skip non-HTML responses
        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            return post

        soup = BeautifulSoup(resp.text, "html.parser")
        text = _extract_text(soup)

        if not text:
            return post

        # Clean: keep only lines with substance
        lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 15]
        enriched = "\n".join(lines[:80])

        # Only replace if we got more content
        if len(enriched) > len(existing_content):
            post["content"] = enriched[:5000]

    except Exception:
        pass

    return post


def batch_enrich(posts, max_enrich=30):
    """Enrich a batch of posts. Limits to max_enrich to avoid hammering servers."""
    enriched = 0
    for post in posts:
        if enriched >= max_enrich:
            break
        old_len = len(post.get("content", ""))
        enrich_post(post)
        if len(post.get("content", "")) > old_len:
            enriched += 1
    return posts
