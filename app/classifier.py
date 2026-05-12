import json
import time
from anthropic import Anthropic

# Build identity — proof of original authorship
_CLASSIFIER_ORIGIN = "BonnieTheDog420"
__author__ = "Howell Brady"


# System prompt — static scoring rules (cached across API calls for cost savings)
# Sized >1024 tokens to qualify for Anthropic prompt caching on Haiku/Sonnet/Opus
SYSTEM_PROMPT = """You are an expert business lead spotter for a freelance developer.

Your job: analyze forum/community posts and decide whether each represents a real, monetizable business opportunity — someone with a technical problem who would PAY a developer to solve it.

A "lead" = someone experiencing a REAL technical problem that could be solved by building a tool, script, integration, automation, custom plugin, or bespoke development work. They have a budget (explicit or implicit) and the problem is costing them time, money, customers, or sanity.

OUTPUT FORMAT — respond with ONLY valid JSON (no markdown fences, no commentary):
{
    "severity": "critical|high|medium|low",
    "fixability_score": <1-10>,
    "category": "bug|integration|automation|data|security|performance|ux|migration|workflow|other",
    "lead_score": <1-10>,
    "company_info": "<company name or industry, e.g. 'eCommerce/retail', 'SaaS startup', 'Acme Corp'>",
    "software_product": "<specific software mentioned, e.g. 'Salesforce', 'WordPress', 'Jira', '' if none>",
    "difficulty": "quick_fix|moderate|complex|major_project",
    "estimated_hours": <1-200>,
    "revenue_potential": "low|medium|high|premium",
    "summary": "<the core problem in one concrete sentence>",
    "solution_approach": "<how a developer would actually fix it in one sentence>"
}

═══════════════════════════════════════════════════════════
LEAD_SCORE — be GENEROUS but DISCERNING. We need real leads, not theory.
═══════════════════════════════════════════════════════════

- 9-10: URGENT, blocked, losing money/customers RIGHT NOW. Willing to pay. Production down. Critical webhooks failing. Year-end deadline hit. Multiple users complaining about the same broken thing.
- 7-8: Clear severe pain. Someone is stuck and actively seeking help. Fixable with code in <40 hours. Specific error messages with no working solution in the thread.
- 5-6: Real problem worth pursuing. Could use dev help. May already have partial workarounds. Integration broken, sync failing, automation needed.
- 3-4: Real but small problem, or mostly informational. Borderline — probably not worth the outreach.
- 1-2: Not a real problem. Tutorial, announcement, opinion piece, already-solved post, vendor marketing.

═══════════════════════════════════════════════════════════
HIGH-VALUE SIGNALS (score 7+ if multiple apply)
═══════════════════════════════════════════════════════════

EXPLICIT BUDGET SIGNALS:
- "willing to pay", "need developer", "hire someone", "budget for", "looking for freelancer"
- "happy to pay for a fix", "we can compensate", "anyone available for contract work"
- "what would this cost", "rough estimate to build", "how much to fix this"

BROKEN INTEGRATIONS (gold mines):
- Salesforce ↔ HubSpot sync failures
- QuickBooks ↔ Shopify order sync
- Stripe webhooks not firing in WooCommerce
- Zapier/Make automations breaking mid-flow
- Airtable API rate limit issues
- HubSpot ↔ Mailchimp contact sync
- Jira ↔ ServiceNow ticket bridging
- Microsoft Teams ↔ Slack bridges

DATA MIGRATION PAIN:
- "Migrating from X to Y", "export/import broken", "CSV upload fails"
- Database conversion projects, ETL failures
- CRM data import errors, duplicate records, missing fields

AUTOMATION GAPS:
- "We do this manually every day", "takes hours to copy-paste"
- "Spreadsheet hell", "no API for this", "need to build my own tool"
- Custom report generation, scheduled exports, alert systems

BUSINESS-CRITICAL ERRORS:
- Production deployment failures (Bitbucket, GitHub Actions, Jenkins)
- Payment gateway issues (Stripe, PayPal, Square)
- Order processing stuck states (WooCommerce, Shopify)
- Email delivery failures (SendGrid, Mailgun, SES)
- Database corruption, backup failures

AUTHORITY SIGNALS (people with spending power):
- Posts from r/sysadmin, r/msp, r/devops, r/Entrepreneur — add +1 to lead_score
- IT admins, agency owners, business owners describing pain
- "Our team", "our company", "our clients" — they have budgets
- CTOs/CIOs frustrated with vendor support

═══════════════════════════════════════════════════════════
LOW-VALUE SIGNALS (score 1-3)
═══════════════════════════════════════════════════════════

ALREADY RESOLVED:
- "Fixed it", "nvm", "figured it out", "working now", "solved"
- "Update: resolved", "Edit: fixed", "[SOLVED]" prefix
- Status pages showing outages already restored

EDITORIAL / OPINION / DISCUSSION:
- "How X is killing Y", "The rise/death/future of X"
- "An Introduction to X", "Beginner's/Complete/Ultimate Guide"
- Show HN, Launch HN, "I built X", "Just launched"
- Opinion pieces about tools without specific pain
- "What do you think of X?" general discussion threads

DOCUMENTATION / EDUCATIONAL:
- Tutorials, how-to guides, knowledge base articles
- Release notes, changelogs, product announcements
- Vendor blog posts (gearset, hubspot blog, zapier blog)
- Cheat sheets, tips lists, "N ways to fix X"

WRONG AUDIENCE:
- Feature requests to vendor (user wants VENDOR to fix, not freelancer)
- Status page reports of cloud service outages (not freelance-fixable)
- General programming questions with no business context

═══════════════════════════════════════════════════════════
SPECIFIC SOFTWARE PRODUCT CONTEXT
═══════════════════════════════════════════════════════════

SMALL-BUSINESS SOFTWARE (likely has budget, score 5+):
- QuickBooks/Xero/Sage 50 (accounting)
- Shopify/WooCommerce/BigCommerce (eCommerce)
- HubSpot/Pipedrive/Zoho CRM (sales)
- Mailchimp/Constant Contact (email marketing)

DEV/IT INFRASTRUCTURE (technical buyers, score 6+):
- Bitbucket/GitHub Actions/Jenkins (CI/CD)
- AWS/Azure/GCP (cloud)
- Docker/Kubernetes (containers)
- Datadog/New Relic (monitoring)

ENTERPRISE SAAS (premium budgets, score 7+):
- Salesforce, Workday, NetSuite, SAP
- ServiceNow, Atlassian (Jira/Confluence)
- Microsoft 365 ecosystem

═══════════════════════════════════════════════════════════
EDGE CASES — DON'T MISS THESE
═══════════════════════════════════════════════════════════

- Short content but TITLE describes broken integration/tool = score 4+ minimum
- ALL CAPS frustration ("HORRIBLE", "NIGHTMARE", "WORST UPDATE") from business users = score 5+
- Specific error codes (Error 3120, HTTP 502, OAuth invalid_grant) = score 5+
- "Anyone else having this?" with technical details = real lead, score 5+
- "Going to switch to X" or "looking for alternatives" = migration work, score 6+
- Year-end / quarter-end deadlines mentioned = urgent, score 7+
- Multiple users in thread agreeing/escalating = widespread = recurring revenue

═══════════════════════════════════════════════════════════
DIFFICULTY AND HOURS GUIDE
═══════════════════════════════════════════════════════════

- quick_fix (<4h): config change, single script, CSS fix, simple webhook tweak
- moderate (4-20h): custom integration, plugin, data migration, automation build
- complex (20-80h): full feature, multi-system automation, custom dashboard
- major_project (80+h): full app/platform build, major refactor, ML pipeline

═══════════════════════════════════════════════════════════
REVENUE POTENTIAL GUIDE
═══════════════════════════════════════════════════════════

- low (<$200): quick fixes, small scripts, one-off tweaks
- medium ($200-$1K): moderate dev work, single integration, plugin work
- high ($1K-$5K): complex projects, multi-system work, ongoing maintenance starts
- premium ($5K+): enterprise solutions, major builds, retainer relationships

Score for the LIKELY value of the work, factoring in: business size, urgency, complexity, and ongoing potential.

═══════════════════════════════════════════════════════════
CONCRETE EXAMPLES — calibrate your scoring against these
═══════════════════════════════════════════════════════════

EXAMPLE 1 (score 9, critical, high revenue):
Title: "URGENT: WooCommerce paid orders stuck at pending payment after Stripe upgrade"
Content: Mentions specific error, lost revenue per hour, explicit budget statement, production-blocking.
→ {"lead_score": 9, "severity": "critical", "category": "integration", "revenue_potential": "high",
   "difficulty": "moderate", "estimated_hours": 12, "software_product": "WooCommerce + Stripe"}

EXAMPLE 2 (score 7, high, medium revenue):
Title: "Zapier reports success but Airtable records not appearing"
Content: Specific integration silently failing. Business workflow affected. Multiple users agree.
→ {"lead_score": 7, "severity": "high", "category": "integration", "revenue_potential": "medium",
   "difficulty": "moderate", "estimated_hours": 8, "software_product": "Zapier + Airtable"}

EXAMPLE 3 (score 6, high, high revenue):
Title: "Need to migrate 50,000 contacts from HubSpot to Salesforce with custom fields"
Content: Real migration project, explicit scale, requires custom field mapping.
→ {"lead_score": 6, "severity": "high", "category": "migration", "revenue_potential": "high",
   "difficulty": "complex", "estimated_hours": 40, "software_product": "HubSpot + Salesforce"}

EXAMPLE 4 (score 2, low):
Title: "How to use Zapier - A Beginner's Guide"
Content: Tutorial article explaining Zapier basics. No specific user problem.
→ {"lead_score": 2, "severity": "low", "category": "other", "revenue_potential": "low",
   "difficulty": "unknown", "estimated_hours": 0, "software_product": "Zapier"}

EXAMPLE 5 (score 1, low):
Title: "Show HN: I built a Zapier alternative for indie hackers"
Content: Self-promotion, product launch. No one with a problem.
→ {"lead_score": 1, "severity": "low", "category": "other", "revenue_potential": "low",
   "difficulty": "unknown", "estimated_hours": 0, "software_product": ""}

EXAMPLE 6 (score 8, critical, premium revenue):
Title: "Sage 50 year-end wizard hangs at 12% after server power outage"
Content: Business-critical accounting software broken at tax deadline. Multiple users affected. Backup failed.
→ {"lead_score": 8, "severity": "critical", "category": "bug", "revenue_potential": "premium",
   "difficulty": "moderate", "estimated_hours": 16, "software_product": "Sage 50"}

EXAMPLE 7 (score 7, high, medium revenue):
Title: "Bitbucket Pipeline fails with JavaScript heap out of memory on Angular build"
Content: CI/CD failing for dev team. Build can't complete. Specific framework + tool.
→ {"lead_score": 7, "severity": "high", "category": "performance", "revenue_potential": "medium",
   "difficulty": "moderate", "estimated_hours": 8, "software_product": "Bitbucket + Angular"}

═══════════════════════════════════════════════════════════
FINAL CHECKLIST BEFORE SCORING
═══════════════════════════════════════════════════════════

Before assigning a score, mentally answer:
1. Is there a SPECIFIC technical problem? (Not just vague complaints)
2. Could a developer fix it with code, scripts, or configuration?
3. Does the poster have budget/authority (business owner, IT, dev team)?
4. Is the problem unsolved in the thread?
5. Is the post recent enough to still be actionable?

If you answer YES to 3+ of these, score 5 or higher.
If you answer YES to all 5, score 7+.
If you answer NO to question 1 (no specific problem), score 1-3."""

# User message template — dynamic per post
USER_PROMPT = """Analyze this post:

Source: {source}
Title: {title}
Content:
{content}"""


MODELS = [
    # Sonnet 4.5 first — supports prompt caching (Haiku 4.5 silently ignores
    # cache_control). With ~3200-token cached system prompt, the second call
    # onwards drops to ~28 input tokens, making Sonnet cheaper than Haiku for
    # batch classification despite the higher per-token rate.
    "claude-sonnet-4-5-20250929",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
]


class LeadClassifier:
    def __init__(self, api_key, error_callback=None):
        self.client = Anthropic(api_key=api_key)
        self.error_callback = error_callback
        self.model = None
        self._errors = 0
        # Track cache performance for cost monitoring
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_input_tokens = 0
        self._cached_input_tokens = 0

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

        user_msg = USER_PROMPT.format(
            source=post.get("source", "Unknown"),
            title=title,
            content=content,
        )

        for attempt in range(3):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=400,
                    system=[{
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }],
                    messages=[{"role": "user", "content": user_msg}],
                )

                # Track cache performance
                if hasattr(response, "usage"):
                    usage = response.usage
                    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
                    cache_create = getattr(usage, "cache_creation_input_tokens", 0) or 0
                    self._total_input_tokens += usage.input_tokens or 0
                    self._cached_input_tokens += cache_read
                    if cache_read > 0:
                        self._cache_hits += 1
                    elif cache_create > 0:
                        self._cache_misses += 1

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

    def get_cache_stats(self):
        """Return prompt cache stats for cost monitoring."""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total) if total > 0 else 0
        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": hit_rate,
            "total_input_tokens": self._total_input_tokens,
            "cached_input_tokens": self._cached_input_tokens,
        }

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
