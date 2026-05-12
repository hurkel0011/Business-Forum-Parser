"""
Local keyword-based pre-scorer. No API needed.
Scores posts based on pain signals, business indicators, and fixability markers.
Use this to pre-filter before sending to Claude (saves time + money).

Author: Howell Brady | Origin: BonnieTheDog420
"""

import re

# Weighted keyword groups — higher weight = stronger lead signal
PAIN_SIGNALS = {
    # Urgent / blocking
    "production down": 8, "critical bug": 8, "losing money": 9,
    "losing customers": 9, "deadline": 6, "urgent": 6,
    "emergency": 7, "blocking": 6, "showstopper": 8,
    "can't work": 7, "business impact": 8, "outage": 7,
    "downtime": 6, "service disruption": 7,

    # Frustration
    "frustrated": 5, "broken": 4, "doesn't work": 5,
    "not working": 4, "stopped working": 5, "still broken": 6,
    "keeps crashing": 5, "keeps failing": 5, "unreliable": 4,
    "terrible": 4, "unusable": 6, "nightmare": 5,
    "pulling my hair": 5, "at my wits end": 6, "desperate": 7,
    "last resort": 6, "fed up": 5, "rage": 4,
    "awful": 4, "garbage": 4, "waste of time": 5,
    "deal breaker": 6, "unacceptable": 5,

    # Seeking help / willing to pay
    "help needed": 4, "any solution": 5, "anyone know": 3,
    "looking for": 3, "need help": 4, "please help": 5,
    "willing to pay": 9, "budget for": 8, "hire someone": 9,
    "need a developer": 9, "looking for freelancer": 9,
    "consulting": 6, "paid solution": 8,
    "can anyone help": 5, "any workaround": 5,
    "anyone else having": 4, "is there a fix": 5,
    "how do i fix": 4, "stuck on": 3,

    # Migration / switching
    "switching from": 6, "looking for alternative": 6,
    "migrating from": 6, "replacing": 5, "moving away from": 6,
    "better alternative": 5, "competitor": 4,
    "considering switching": 6, "about to cancel": 7,
    "canceling subscription": 7,
    "hate this": 5, "worst software": 6, "regret": 5,

    # Explicit help-seeking (very high value)
    "anyone recommend": 4, "what do you use": 3,
    "can someone build": 9, "need someone to": 7,
    "contractor": 6, "freelance": 5,

    # Integration problems
    "integration": 4, "api issue": 5, "api broken": 6,
    "webhook": 4, "sync issue": 5, "data sync": 4,
    "connector broken": 6, "integration broken": 7,
    "doesn't integrate": 5, "no integration": 4,
    "zapier": 4, "automation broken": 6,
    "api error": 5, "api rate limit": 5, "oauth": 4,
    "rest api": 4, "graphql": 3, "sdk": 3,

    # Workflow / process
    "manual process": 5, "time consuming": 4, "repetitive": 4,
    "workflow broken": 6, "bottleneck": 5, "inefficient": 4,
    "takes hours": 5, "need automation": 7, "automate": 5,
    "spreadsheet hell": 6, "copy paste": 4,
    "tedious": 4, "workaround": 4, "hacky": 4,

    # Data problems
    "data loss": 7, "data migration": 5, "data export": 4,
    "data import": 4, "csv import": 3, "database issue": 5,
    "corrupt": 6, "data integrity": 5,
    "lost data": 7, "backup failed": 6,

    # Error messages (strong signal of real technical problems)
    "error 500": 5, "error 502": 5, "error 503": 5,
    "error 522": 5, "error 404": 3, "timeout": 4,
    "stack trace": 4, "exception": 3, "traceback": 4,
    "segfault": 5, "null pointer": 4, "memory leak": 5,
    "crash report": 5,
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
    "zendesk": 3, "freshdesk": 3, "intercom": 3,
    "stripe": 3, "paypal": 2, "square": 2,
    "notion": 2, "airtable": 3, "monday.com": 3,
    "production environment": 5, "staging": 3,
    "deployment": 3, "ci/cd": 3, "pipeline": 3,
}

FIXABLE_MARKERS = {
    "script": 3, "code": 2, "api": 3,
    "plugin": 3, "extension": 3, "integration": 3,
    "automation": 4, "bot": 3, "webhook": 3,
    "dashboard": 3, "report": 2, "export": 2,
    "migration tool": 4, "converter": 3, "scraper": 3,
    "connector": 3, "middleware": 3, "bridge": 3,
    "custom solution": 5, "workaround": 3,
    "configuration": 3, "settings": 2, "config": 2,
    "workflow": 3, "template": 2, "form": 2,
    "database": 3, "query": 2, "sql": 3,
    "css": 2, "html": 2, "javascript": 3,
    "python": 3, "node": 3, "react": 3,
}

NEGATIVE_SIGNALS = {
    # Already resolved
    "solved": -5, "fixed it": -5, "nvm": -6, "never mind": -6,
    "figured it out": -5, "working now": -5, "resolved": -5,
    "update: fixed": -6, "edit: solved": -6,
    # Educational / tutorials (not someone with a problem)
    "tutorial": -3, "how to": -2, "eli5": -3,
    "step by step": -3, "beginner's guide": -4, "getting started": -3,
    "cheat sheet": -4, "tips and tricks": -3,
    "common errors and how to fix": -5, "error messages and how to": -5,
    "best practices": -3,
    # Opinion / editorial / discussion
    "opinion": -3, "what do you think": -2, "discussion": -2,
    "is killing": -3, "is shaping": -4, "the future of": -3,
    "the rise of": -4, "the death of": -4, "the state of": -3,
    "hot take": -4, "unpopular opinion": -4,
    "meme": -6, "joke": -5, "shower thought": -6,
    "hiring": -2, "job posting": -3,
    # Documentation / not a complaint
    "documentation": -2, "changelog": -4, "release notes": -4,
    "announcement": -3, "blog post": -2,
    # Show / Launch / product promotion (not complaints)
    "show hn": -6, "launch hn": -6, "tell hn": -3,
    "i built": -4, "i made": -4, "just launched": -5,
    "introducing": -4, "we're excited": -5, "now available": -4,
    "open source": -2, "side project": -3,
    # Career / general life (not technical problems)
    "career advice": -4, "resume": -3, "interview": -3,
    "salary": -3, "job market": -4, "laid off": -3,
    "i wrote a": -3, "i created a": -3,
    # News / journalism
    "according to": -2, "report says": -3, "study finds": -3,
    "researchers": -3, "experts say": -3,
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
    if content_len > 300:
        score += 1
    if content_len > 500:
        score += 2
    if content_len > 1000:
        score += 2
    if content_len > 2000:
        score += 1

    # Bonus for question marks (asking for help)
    question_marks = text.count("?")
    if question_marks >= 1:
        score += 1
    if question_marks >= 3:
        score += 2

    # Bonus for exclamation marks (frustration)
    if text.count("!") >= 2:
        score += 1

    # Bonus for ALL CAPS words (frustration signal)
    caps_words = len(re.findall(r'\b[A-Z]{4,}\b', post.get("content", "")))
    if caps_words >= 2:
        score += 2

    # Penalty for article/editorial titles (not someone with a problem)
    title = post.get("title", "").lower()
    editorial_patterns = [
        r"^how .+ is (killing|changing|shaping|transforming|disrupting)",
        r"^the (rise|death|future|state|end) of ",
        r"^why .+ (is|are) (dead|dying|overrated|wrong)",
        r"^\d+ (ways|tips|steps|things|reasons) ",
        r"^(a|the) .+ guide to ",
        r"common .+ errors? .+ (fix|solv|resolv)",
        r"^what .+ taught me",
        r"^i (wrote|built|made|created) (a|an|my|the) ",
        r"^gaming on ",
        r"explained",
    ]
    for pat in editorial_patterns:
        if re.search(pat, title):
            score -= 4
            break

    # Bonus for forum/community source URLs
    url = post.get("url", "").lower()
    forum_signals = ["community.", "forum.", "discuss.", "support.",
                     "reddit.com", "stackoverflow.com", "github.com/issues"]
    if any(s in url for s in forum_signals):
        score += 2

    # Bonus for recency signals in content
    recency_patterns = [
        "2026", "2025", "today", "yesterday", "this week",
        "this month", "just now", "recently", "still happening",
        "still broken", "update:", "edit:",
    ]
    if any(p in text for p in recency_patterns):
        score += 2

    # Normalize to 0-10 using a curve that spreads values better
    # Raw scores: 0-10 = low, 10-25 = medium, 25-50 = high, 50+ = very high
    if score <= 0:
        normalized = 0
    elif score <= 10:
        normalized = score * 0.3  # 0-3
    elif score <= 25:
        normalized = 3 + (score - 10) * 0.27  # 3-7
    elif score <= 50:
        normalized = 7 + (score - 25) * 0.12  # 7-10
    else:
        normalized = 10.0
    normalized = max(0, min(10, normalized))

    post["_prescore"] = round(normalized, 1)
    post["_matched_keywords"] = matched_keywords[:15]

    return normalized


def batch_prescore(posts, min_score=1.5):
    """Pre-score and filter a list of posts. Returns sorted by score."""
    for post in posts:
        prescore(post)

    filtered = [p for p in posts if p.get("_prescore", 0) >= min_score]
    filtered.sort(key=lambda p: p.get("_prescore", 0), reverse=True)

    return filtered
