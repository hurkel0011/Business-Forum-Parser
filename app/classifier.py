import json
import time
from anthropic import Anthropic

# Build identity — proof of original authorship
_CLASSIFIER_ORIGIN = "BonnieTheDog420"
__author__ = "Howell Brady"


CLASSIFY_PROMPT = """You are a business lead spotter. Analyze this forum/community post and decide if it represents a real business opportunity for a freelance developer.

A "lead" = someone experiencing a REAL technical problem that could be solved by building a tool, script, integration, automation, or custom development.

Post Source: {source}
Post Title: {title}
Post Content:
{content}

Respond with ONLY valid JSON (no markdown, no explanation):
{{
    "severity": "critical|high|medium|low",
    "fixability_score": <1-10>,
    "category": "bug|integration|automation|data|security|performance|ux|migration|workflow|other",
    "lead_score": <1-10>,
    "company_info": "<company name or industry, e.g. 'Acme Corp' or 'eCommerce/retail'>",
    "software_product": "<specific software mentioned, e.g. 'Salesforce', 'WordPress', 'Jira', or ''>",
    "difficulty": "quick_fix|moderate|complex|major_project",
    "estimated_hours": <best guess hours to fix: 1-200>,
    "revenue_potential": "low|medium|high|premium",
    "summary": "<the core problem in one sentence>",
    "solution_approach": "<how a developer would fix it in one sentence>"
}}

SCORING RULES — be generous, we want to catch opportunities:
- 8-10: URGENT pain — blocked, losing money, willing to pay, needs developer
- 6-7: Clear pain point, someone is stuck and actively seeking help, fixable with code
- 4-5: Real problem mentioned, could use dev help, but may already have partial solutions
- 2-3: Vague issue, already solved, or purely informational
- 1: Not a problem at all (documentation, announcement, marketing)

IMPORTANT: Score 5+ if ANY of these are true:
- A business user describes a specific broken workflow or integration
- Someone is comparing/switching tools due to pain (they'll pay for migration help)
- A recurring or widespread issue that affects multiple users (community thread with agreements)
- Someone describes manual/tedious processes that could be automated
- Error messages or bugs in production that are unsolved

HIGH-VALUE SIGNALS (score 6+):
- "willing to pay", "need developer", "hire someone", "budget"
- Broken integrations between TWO specific products (e.g. "Salesforce + HubSpot sync")
- Data migration pain, export/import failures between systems
- Automation that stopped working or doesn't exist yet
- Business-critical workflows that are manual or broken
- Specific error codes or stack traces with unsolved problems
- Multiple users reporting the same issue (widespread = recurring revenue)
- "Anyone else having this problem?" + technical details = real lead
- IT admins or business owners describing tool pain (they have budgets)

LOW-VALUE SIGNALS (score 1-3):
- Already solved/resolved posts ("fixed it", "nvm", "working now")
- Official documentation or knowledge base articles
- Marketing pages, product announcements, changelogs
- General "how to" tutorials without a specific problem
- Discussions about preferences/opinions without actionable pain
- Status pages or outage reports for cloud services (not fixable by a dev)
- Feature requests to the vendor (user wants vendor to fix, not a freelancer)

IMPORTANT EDGE CASES — don't miss these:
- If content is short but the TITLE describes a specific broken integration/tool, score 4+ (the title alone signals real pain)
- QuickBooks/Xero/Shopify users complaining = small business owners with budgets, score 5+
- "HORRIBLE", "NIGHTMARE", "worst update" from business users = score 5+ (they'll pay to fix it)
- CI/CD pipeline failures (Bitbucket, GitHub Actions, Jenkins) = dev teams who pay for DevOps help, score 5+
- Broken webhooks, API rate limits, sync failures = integration work, always score 5+
- Posts from r/sysadmin, r/msp = IT professionals with company budgets, add +1 to score

DIFFICULTY GUIDE:
- quick_fix: Under 4 hours — config change, small script, CSS fix, simple bug
- moderate: 4-20 hours — custom integration, plugin, data migration
- complex: 20-80 hours — full feature build, multi-system automation
- major_project: 80+ hours — full app/platform, major overhaul

REVENUE POTENTIAL:
- low: Under $200 — quick fixes, small scripts
- medium: $200-$1000 — moderate dev work, integrations
- high: $1000-$5000 — complex projects, ongoing maintenance
- premium: $5000+ — enterprise solutions, major builds"""


MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-5-20250929",
    "claude-sonnet-4-6",
]


class LeadClassifier:
    def __init__(self, api_key, error_callback=None):
        self.client = Anthropic(api_key=api_key)
        self.error_callback = error_callback
        self.model = None
        self._errors = 0

    # Pain signal words for smart content truncation
    _PAIN_WORDS = {
        "error", "broken", "broken", "failed", "failing", "crash",
        "bug", "issue", "problem", "help", "frustrated", "urgent",
        "blocked", "stuck", "not working", "doesn't work", "stopped",
        "integration", "api", "webhook", "sync", "migrate", "migration",
        "workaround", "fix", "desperate", "losing", "money", "pay",
    }

    def _report(self, msg):
        if self.error_callback:
            self.error_callback(msg)

    @staticmethod
    def _smart_truncate(content, max_len):
        """Extract the most relevant paragraphs instead of blind truncation.

        Prioritizes paragraphs that contain pain signals, error messages, or
        technical details over generic introduction text.
        """
        paragraphs = [p.strip() for p in content.split("\n") if len(p.strip()) > 20]

        if not paragraphs:
            return content[:max_len]

        # Score each paragraph by pain relevance
        pain_words = LeadClassifier._PAIN_WORDS
        scored = []
        for i, para in enumerate(paragraphs):
            para_lower = para.lower()
            score = sum(1 for w in pain_words if w in para_lower)
            # Boost first paragraph (context) and any with error codes
            if i == 0:
                score += 2
            if any(c in para for c in ["500", "404", "403", "ERROR", "Exception", "Traceback"]):
                score += 3
            scored.append((score, i, para))

        # Sort by relevance, keeping position info
        scored.sort(key=lambda x: (-x[0], x[1]))

        # Take the most relevant paragraphs, up to max_len
        selected = []
        total = 0
        for _score, _idx, para in scored:
            if total + len(para) + 1 > max_len:
                break
            selected.append((_idx, para))
            total += len(para) + 1

        # Re-sort by original position for readability
        selected.sort(key=lambda x: x[0])

        return "\n".join(p for _, p in selected)

    def _find_working_model(self):
        """Try each model until one works."""
        for model in MODELS:
            try:
                resp = self.client.messages.create(
                    model=model,
                    max_tokens=50,
                    messages=[{"role": "user", "content": "Say OK"}],
                )
                if resp.content:
                    self._report(f"Using model: {model}")
                    return model
            except Exception as e:
                self._report(f"Model {model} failed: {e}")
                continue
        return None

    def classify(self, post):
        if self.model is None:
            self.model = self._find_working_model()
            if self.model is None:
                self._report("ERROR: No working Claude model found. Check your API key.")
                return self._fallback("No working model")

        content = post.get("content", "") or ""
        title = post.get("title", "") or ""

        if len(content) < 20:
            content = title

        # Smart content preparation — prioritize pain-signal paragraphs
        if len(content) > 2500:
            content = self._smart_truncate(content, 2500)

        prompt = CLASSIFY_PROMPT.format(
            source=post.get("source", "Unknown"),
            title=title,
            content=content,
        )

        for attempt in range(3):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=400,
                    messages=[{"role": "user", "content": prompt}],
                )

                text = response.content[0].text.strip()

                # Strip markdown fences
                if text.startswith("```"):
                    text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

                # Try to parse JSON from response
                json_text = text
                if not json_text.startswith("{"):
                    start = json_text.find("{")
                    end = json_text.rfind("}") + 1
                    if start >= 0 and end > start:
                        json_text = json_text[start:end]

                if json_text.startswith("{"):
                    try:
                        result = json.loads(json_text)
                        self._errors = 0
                        return result
                    except json.JSONDecodeError:
                        # Try to fix common issues: trailing commas, extra data
                        # Find the matching closing brace for the first opening brace
                        depth = 0
                        for idx, ch in enumerate(json_text):
                            if ch == "{":
                                depth += 1
                            elif ch == "}":
                                depth -= 1
                                if depth == 0:
                                    try:
                                        result = json.loads(json_text[:idx + 1])
                                        self._errors = 0
                                        return result
                                    except json.JSONDecodeError:
                                        break
                        pass  # fall through to retry

                self._report(f"Bad JSON response: {text[:100]}")

            except json.JSONDecodeError as e:
                self._report(f"JSON parse error: {e}")
            except Exception as e:
                err_str = str(e)
                self._errors += 1

                if "rate_limit" in err_str.lower() or "429" in err_str:
                    wait = 5 * (attempt + 1)
                    self._report(f"Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                    continue

                if "overloaded" in err_str.lower():
                    wait = 3 * (attempt + 1)
                    self._report(f"API overloaded, waiting {wait}s...")
                    time.sleep(wait)
                    continue

                if "not_found" in err_str.lower() or "404" in err_str:
                    # Model deprecated — try next one
                    self._report(f"Model {self.model} not found, trying next...")
                    self.model = self._find_working_model()
                    if self.model is None:
                        return self._fallback("All models deprecated")
                    continue

                self._report(f"API error: {err_str[:150]}")

                if self._errors > 8:
                    self._report("Too many errors, stopping classification")
                    return self._fallback(err_str)

        return self._fallback("Max retries reached")

    def _fallback(self, reason):
        return {
            "severity": "unknown",
            "fixability_score": 0,
            "category": "unknown",
            "lead_score": 0,
            "company_info": "unknown",
            "software_product": "",
            "difficulty": "unknown",
            "estimated_hours": 0,
            "revenue_potential": "unknown",
            "summary": f"Classification failed: {reason}",
            "solution_approach": "",
        }
