import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}


def enrich_post(post):
    """Fetch the actual page content for a post to give the classifier more to work with."""
    url = post.get("url", "")
    if not url or len(post.get("content", "")) > 300:
        return post

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        if resp.status_code != 200:
            return post

        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        # Try to find the main content area
        main = (
            soup.select_one("article")
            or soup.select_one('[role="main"]')
            or soup.select_one(".post-content, .question-body, .message-body")
            or soup.select_one("#content, .content, main")
            or soup.select_one(".lia-message-body, .s-prose")
            or soup.body
        )

        if main:
            text = main.get_text(separator="\n", strip=True)
            lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 20]
            enriched = "\n".join(lines[:50])

            if len(enriched) > len(post.get("content", "")):
                post["content"] = enriched[:3000]

    except Exception:
        pass

    return post
