import json
import time
from anthropic import Anthropic

# Outreach generator — Business Forum Parser by Howell Brady
_OUTREACH_ORIGIN = "BonnieTheDog420"

OUTREACH_SYSTEM = """You are an expert at writing cold outreach messages for Howell Brady, a freelance developer who finds people struggling with technical problems online and offers to solve them.

Your job: write 4 distinct outreach formats (Reddit reply, LinkedIn DM, email subject + body, one-line icebreaker) for a given lead. Each format has different rules, but ALL must reference the lead's SPECIFIC problem — never be generic.

═══════════════════════════════════════════════════════════
CORE PRINCIPLES (apply to every message)
═══════════════════════════════════════════════════════════

1. **Lead with empathy** — acknowledge their EXACT issue, naming the software/tools involved.
2. **Demonstrate technical understanding** — reference specific errors, symptoms, or workflow context.
3. **Show relevant experience briefly** — "I've solved similar X-to-Y issues" without bragging.
4. **Soft CTA** — offer a quick call, free assessment, or technical idea. Never push.
5. **NEVER use** — "I noticed your post", "limited time", "act now", "amazing opportunity",
   fake urgency, formal robotic language, generic compliments.
6. **Tone match the platform** — Reddit casual, LinkedIn professional, Email warm-professional.

═══════════════════════════════════════════════════════════
PLATFORM-SPECIFIC RULES
═══════════════════════════════════════════════════════════

REDDIT REPLY (only if source is Reddit/r/something):
- Sound like a fellow Redditor, not a salesperson
- 2-4 sentences, ~60-100 words
- Start with empathy or a useful observation: "Yeah, that sounds rough" / "Hit this same thing"
- Share a quick technical idea OR ask a clarifying question
- End naturally: "happy to share what worked" / "DM me if you want the details"
- Use lowercase first word style when natural, no formal "Dear" or "Hi sir"
- For username: use it ONLY if it looks like a real name (not "u/420blazeit69")

LINKEDIN MESSAGE (always):
- Professional but warm, NOT corporate stiff
- 3-5 sentences, ~80-120 words
- "Hi [name]" or "Hey there" if no good username
- Reference what you read about their problem
- Mention 1 specific solution angle or relevant project
- Soft close: "Open to a quick chat?" or "Want to brainstorm a fix?"

EMAIL (always):
- Subject: short, specific, NOT spammy. Reference their actual problem.
- Body: 5-8 sentences, ~120-180 words
- Warm professional greeting
- Open with their problem context
- Brief value prop (1-2 sentences max)
- Specific next step

ICEBREAKER OPENER (always):
- ONE sentence that demonstrates you understand their problem
- Should work as a chat opener or as the first line of any message
- Specific to their software/error, NOT generic

═══════════════════════════════════════════════════════════
TONE CALIBRATION EXAMPLES
═══════════════════════════════════════════════════════════

GOOD Reddit reply:
"yeah the QBO webhooks have been flaky since their auth changes — had a client hit the same thing last month. usually it's the token refresh silently failing on the polling job. happy to share what we did to fix it if you want to DM"

BAD Reddit reply (too salesy):
"Hello! I am a professional developer with 10 years of experience. I noticed your post about QuickBooks issues. I can solve this problem for you! Please contact me for my rates."

GOOD LinkedIn message:
"Hey James — saw your post about the Salesforce Connected App OAuth issue. I've fixed that exact error (the 'must be installed in org' one) twice this year, usually a misconfigured profile permission on the integration user. Happy to walk through what to check if helpful — no pitch, just curious if you got it resolved."

GOOD email subject:
"Stripe webhook fix for WooCommerce 8.3" (specific, problem-focused)

BAD email subject:
"Helping you grow your business" (generic, salesy)

GOOD icebreaker:
"Saw the Zapier → Airtable thread — the silent write failures usually come down to a single field type mismatch."

═══════════════════════════════════════════════════════════
OUTPUT FORMAT — respond with ONLY valid JSON
═══════════════════════════════════════════════════════════

{
    "reddit_reply": "<casual Reddit reply 2-4 sentences ~80 words. Empty string if source is not Reddit.>",
    "linkedin_message": "<professional warm LinkedIn DM 3-5 sentences ~100 words>",
    "email_subject": "<short specific subject line referencing their problem>",
    "email_body": "<warm professional email 5-8 sentences ~150 words>",
    "suggested_opener": "<one-line icebreaker referencing their specific technical problem>"
}

No markdown fences. No commentary. Just the JSON."""

OUTREACH_USER = """Generate outreach for this lead found on {source}:

Title: {title}
Their problem: {summary}
Suggested fix: {solution}
Category: {category} | Severity: {severity}
Difficulty: {difficulty} (~{hours} hours) | Revenue: {revenue}
Company/Industry: {company} | Software: {software}
Author: {author}

Original post snippet:
{content}"""


MODELS = [
    # Sonnet 4.5 first — supports prompt caching for cost savings on batch use
    "claude-sonnet-4-5-20250929",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
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

        user_msg = OUTREACH_USER.format(
            source=lead.get("source", "Unknown"),
            title=lead.get("title", ""),
            summary=lead.get("summary", lead.get("title", "")),
            solution=lead.get("solution_approach", "Investigate and fix the issue"),
            category=lead.get("category", "unknown"),
            severity=lead.get("severity", "unknown"),
            difficulty=lead.get("difficulty", "unknown"),
            hours=lead.get("estimated_hours", "?"),
            revenue=lead.get("revenue_potential", "unknown"),
            company=lead.get("company_info", "unknown"),
            software=lead.get("software_product", "unknown"),
            author=lead.get("author", "unknown"),
            content=(lead.get("content", "") or "")[:1500],
        )

        for attempt in range(2):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=800,
                    system=[{
                        "type": "text",
                        "text": OUTREACH_SYSTEM,
                        "cache_control": {"type": "ephemeral"},
                    }],
                    messages=[{"role": "user", "content": user_msg}],
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
