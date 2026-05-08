import json
import time
from anthropic import Anthropic

# Outreach generator — Business Forum Parser by Howell Brady
_OUTREACH_ORIGIN = "BonnieTheDog420"

OUTREACH_PROMPT = """You are an expert at writing cold outreach messages for a freelance developer who finds people
struggling with technical problems online and offers to solve them.

Here is a lead found on {source}:

Title: {title}
Their problem: {summary}
Suggested fix: {solution}
Category: {category}
Severity: {severity}
Company/Industry: {company}

Original post snippet:
{content}

Generate TWO outreach messages. Make them sound human, helpful, NOT salesy.
Reference their SPECIFIC problem — never be generic. Keep it casual but professional.

Rules:
- Lead with empathy about their specific issue
- Briefly mention you can help (don't oversell)
- End with a soft call to action (offer a quick call or free assessment)
- No fake urgency, no "limited time offers"
- Sound like a real person, not a template
- Use their name if visible, otherwise "Hi there"

Respond with ONLY valid JSON:
{{
    "linkedin_message": "<Short LinkedIn DM, 3-5 sentences max, ~100 words>",
    "email_subject": "<Email subject line, short and specific>",
    "email_body": "<Professional email, 5-8 sentences, ~150 words>",
    "suggested_opener": "<One-line icebreaker referencing their post>"
}}"""


MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-5-20250929",
    "claude-sonnet-4-6",
]


class OutreachGenerator:
    def __init__(self, api_key, error_callback=None):
        self.client = Anthropic(api_key=api_key)
        self.error_callback = error_callback
        self.model = None

    def _report(self, msg):
        if self.error_callback:
            self.error_callback(msg)

    def _find_working_model(self):
        for model in MODELS:
            try:
                resp = self.client.messages.create(
                    model=model,
                    max_tokens=50,
                    messages=[{"role": "user", "content": "Say OK"}],
                )
                if resp.content:
                    return model
            except Exception:
                continue
        return None

    def generate(self, lead):
        """Generate outreach messages for a lead. Returns dict with linkedin_message, email_subject, email_body, suggested_opener."""
        if self.model is None:
            self.model = self._find_working_model()
            if self.model is None:
                self._report("No working Claude model found.")
                return self._fallback(lead)

        prompt = OUTREACH_PROMPT.format(
            source=lead.get("source", "Unknown"),
            title=lead.get("title", ""),
            summary=lead.get("summary", lead.get("title", "")),
            solution=lead.get("solution_approach", "Investigate and fix the issue"),
            category=lead.get("category", "unknown"),
            severity=lead.get("severity", "unknown"),
            company=lead.get("company_info", "unknown"),
            content=(lead.get("content", "") or "")[:1500],
        )

        for attempt in range(2):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}],
                )

                text = response.content[0].text.strip()

                # Strip markdown fences
                if text.startswith("```"):
                    text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

                # Find JSON
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    result = json.loads(text[start:end])
                    return result

                self._report(f"Bad response format, retrying...")

            except json.JSONDecodeError:
                self._report("JSON parse error, retrying...")
            except Exception as e:
                err = str(e)
                if "rate_limit" in err.lower() or "429" in err:
                    self._report("Rate limited, waiting 5s...")
                    time.sleep(5)
                    continue
                if "overloaded" in err.lower():
                    self._report("API overloaded, waiting 3s...")
                    time.sleep(3)
                    continue
                self._report(f"API error: {err[:150]}")

        return self._fallback(lead)

    def _fallback(self, lead):
        """Generate a basic template if API fails."""
        title = lead.get("title", "your post")
        source = lead.get("source", "online")
        return {
            "linkedin_message": (
                f"Hi there - I came across your post about \"{title[:60]}\" on {source}. "
                f"I'm a developer who specializes in exactly this kind of issue. "
                f"Would you be open to a quick chat about how I might help?"
            ),
            "email_subject": f"Re: {title[:50]}",
            "email_body": (
                f"Hi,\n\n"
                f"I saw your post about \"{title[:60]}\" on {source} and it caught my eye - "
                f"I've solved similar problems for other businesses.\n\n"
                f"I'd love to learn more about what you're dealing with and see if I can help. "
                f"Would you be open to a quick 15-minute call this week?\n\n"
                f"Best regards"
            ),
            "suggested_opener": f"Saw your post about \"{title[:50]}\" - I think I can help.",
        }
