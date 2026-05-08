import json
import time
from anthropic import Anthropic

# Build identity — proof of original authorship
_CLASSIFIER_ORIGIN = "BonnieTheDog420"
__author__ = "Howell Brady"


CLASSIFY_PROMPT = """You are a business opportunity spotter. Analyze this forum post and score it as a lead.

A "lead" = someone with a REAL technical problem that a freelance developer could fix and sell as a service/tool.

Post Source: {source}
Post Title: {title}
Post Content:
{content}

Respond with ONLY valid JSON:
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
    "summary": "<the problem in one sentence>",
    "solution_approach": "<how a developer would fix it in one sentence>"
}}

SCORING RULES - be generous:
- 7-10: Clear pain point, someone is stuck, fixable with code/automation
- 4-6: Real problem mentioned, might need dev help
- 2-3: Vague issue or already partly solved
- 1: No real problem at all

DIFFICULTY GUIDE:
- quick_fix: Under 4 hours — config change, small script, CSS fix, simple bug
- moderate: 4-20 hours — custom integration, plugin development, data migration
- complex: 20-80 hours — full feature build, complex automation, multi-system work
- major_project: 80+ hours — full app/platform, major overhaul

REVENUE POTENTIAL:
- low: Under $200 — quick fixes, small scripts
- medium: $200-$1000 — moderate dev work, integrations
- high: $1000-$5000 — complex projects, ongoing maintenance
- premium: $5000+ — enterprise solutions, major builds

Extract the SPECIFIC software product name if one is mentioned (Salesforce, WordPress, Jira, Shopify, etc.).
Extract the company name or industry if identifiable.
If you can imagine ANY way a developer could help this person, score it 4+."""


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

    def _report(self, msg):
        if self.error_callback:
            self.error_callback(msg)

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

        prompt = CLASSIFY_PROMPT.format(
            source=post.get("source", "Unknown"),
            title=title,
            content=content[:2500],
        )

        for attempt in range(2):
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
                if text.startswith("{") and text.endswith("}"):
                    result = json.loads(text)
                    self._errors = 0
                    return result

                # Try to find JSON in the response
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    result = json.loads(text[start:end])
                    self._errors = 0
                    return result

                self._report(f"Bad JSON response: {text[:100]}")

            except json.JSONDecodeError as e:
                self._report(f"JSON parse error: {e}")
            except Exception as e:
                err_str = str(e)
                self._errors += 1

                if "rate_limit" in err_str.lower() or "429" in err_str:
                    self._report("Rate limited, waiting 5s...")
                    time.sleep(5)
                    continue

                if "overloaded" in err_str.lower():
                    self._report("API overloaded, waiting 3s...")
                    time.sleep(3)
                    continue

                self._report(f"API error: {err_str[:150]}")

                if self._errors > 5:
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
            "summary": f"Classification failed: {reason}",
            "solution_approach": "",
        }
