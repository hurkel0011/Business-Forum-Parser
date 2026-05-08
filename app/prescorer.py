"""
Local keyword-based pre-scorer. No API needed.
Scores posts based on pain signals, business indicators, and fixability markers.
Use this to pre-filter before sending to Claude (saves time + money).
"""

import re

# Weighted keyword groups — higher weight = stronger lead signal
PAIN_SIGNALS = {
    # Urgent / blocking
    "production down": 8, "critical bug": 8, "losing money": 9,
    "losing customers": 9, "deadline": 6, "urgent": 6,
    "emergency": 7, "blocking": 6, "showstopper": 8,
    "can't work": 7, "business impact": 8, "outage": 7,

    # Frustration
    "frustrated": 5, "broken": 4, "doesn't work": 5,
    "not working": 4, "stopped working": 5, "still broken": 6,
    "keeps crashing": 5, "keeps failing": 5, "unreliable": 4,
    "terrible": 4, "unusable": 6, "nightmare": 5,
    "pulling my hair": 5, "at my wits end": 6, "desperate": 7,
    "last resort": 6, "fed up": 5,

    # Seeking help / willing to pay
    "help needed": 4, "any solution": 5, "anyone know": 3,
    "looking for": 3, "need help": 4, "please help": 5,
    "willing to pay": 9, "budget for": 8, "hire someone": 9,
    "need a developer": 9, "looking for freelancer": 9,
    "consulting": 6, "paid solution": 8,

    # Migration / switching
    "switching from": 6, "looking for alternative": 6,
    "migrating from": 6, "replacing": 5, "moving away from": 6,
    "better alternative": 5, "competitor": 4,

    # Integration problems
    "integration": 4, "api issue": 5, "api broken": 6,
    "webhook": 4, "sync issue": 5, "data sync": 4,
    "connector broken": 6, "integration broken": 7,
    "doesn't integrate": 5, "no integration": 4,
    "zapier": 4, "automation broken": 6,

    # Workflow / process
    "manual process": 5, "time consuming": 4, "repetitive": 4,
    "workflow broken": 6, "bottleneck": 5, "inefficient": 4,
    "takes hours": 5, "need automation": 7, "automate": 5,
    "spreadsheet hell": 6, "copy paste": 4,

    # Data problems
    "data loss": 7, "data migration": 5, "data export": 4,
    "data import": 4, "csv import": 3, "database issue": 5,
    "corrupt": 6, "data integrity": 5,
}

BUSINESS_INDICATORS = {
    "enterprise": 3, "company": 2, "business": 2,
    "team": 2, "organization": 2, "department": 2,
    "client": 3, "customer": 2, "revenue": 4,
    "saas": 3, "startup": 2, "small business": 3,
    "e-commerce": 3, "ecommerce": 3, "shop": 2,
    "agency": 3, "firm": 2, "corp": 2,
    "employees": 3, "users": 2, "accounts": 2,
    "subscription": 3, "pricing": 2, "invoice": 3,
    "crm": 3, "erp": 3, "salesforce": 4,
    "hubspot": 3, "quickbooks": 3, "shopify": 3,
    "microsoft teams": 3, "slack": 2, "jira": 3,
}

FIXABLE_MARKERS = {
    "script": 3, "code": 2, "api": 3,
    "plugin": 3, "extension": 3, "integration": 3,
    "automation": 4, "bot": 3, "webhook": 3,
    "dashboard": 3, "report": 2, "export": 2,
    "migration tool": 4, "converter": 3, "scraper": 3,
    "connector": 3, "middleware": 3, "bridge": 3,
    "custom solution": 5, "workaround": 3,
}

NEGATIVE_SIGNALS = {
    "solved": -5, "fixed it": -5, "nvm": -6, "never mind": -6,
    "figured it out": -5, "working now": -5, "resolved": -5,
    "tutorial": -3, "how to": -2, "eli5": -3,
    "opinion": -3, "what do you think": -2, "discussion": -2,
    "meme": -6, "joke": -5, "shower thought": -6,
    "hiring": -2, "job posting": -3,
}


def prescore(post):
    """Score a post locally using keyword matching. Returns 0-10."""
    text = f"{post.get('title', '')} {post.get('content', '')}".lower()

    if len(text) < 30:
        return 0

    score = 0
    matched_keywords = []

    for keywords_dict in [PAIN_SIGNALS, BUSINESS_INDICATORS, FIXABLE_MARKERS]:
        for keyword, weight in keywords_dict.items():
            if keyword.lower() in text:
                score += weight
                matched_keywords.append(keyword)

    for keyword, weight in NEGATIVE_SIGNALS.items():
        if keyword.lower() in text:
            score += weight

    # Bonus for longer content (more detail = more real problem)
    content_len = len(post.get("content", ""))
    if content_len > 500:
        score += 2
    if content_len > 1000:
        score += 2

    # Bonus for question marks (asking for help)
    question_marks = text.count("?")
    if question_marks >= 2:
        score += 2

    # Normalize to 0-10
    normalized = max(0, min(10, score / 4))

    post["_prescore"] = round(normalized, 1)
    post["_matched_keywords"] = matched_keywords[:10]

    return normalized


def batch_prescore(posts, min_score=1.5):
    """Pre-score and filter a list of posts. Returns sorted by score."""
    for post in posts:
        prescore(post)

    filtered = [p for p in posts if p.get("_prescore", 0) >= min_score]
    filtered.sort(key=lambda p: p.get("_prescore", 0), reverse=True)

    return filtered
