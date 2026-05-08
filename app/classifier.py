import json
import time
from anthropic import Anthropic


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
    "company_info": "<guess company/industry or 'unknown'>",
    "summary": "<the problem in one sentence>",
    "solution_approach": "<how to fix it in one sentence>"
}}

SCORING RULES - be generous:
- 7-10: Clear pain point, someone is stuck, fixable with code/automation
- 4-6: Real problem mentioned, might need dev help
- 2-3: Vague issue or already partly solved
- 1: No real problem at all

If you can imagine ANY way a developer could help this person, score it 4+."""


MODELS = [
    "claude-sonnet-4-20250514",
    "claude-3-5-sonnet-20241022",
    "claude-3-haiku-20240307",
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
