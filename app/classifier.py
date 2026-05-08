import json
from anthropic import Anthropic


CLASSIFY_PROMPT = """You are a business lead scorer. Analyze this forum post and rate it as a potential lead — someone who has a problem that a freelance developer could fix and sell as a service.

Be GENEROUS with scoring. If there's ANY indication of a real problem that code could solve, score it 4+. Only score below 3 if the post is clearly irrelevant (off-topic, already solved, just a discussion with no problem).

Post Source: {source}
Post Title: {title}
Post Content:
{content}

Author: {author}

Score this lead. Respond with ONLY valid JSON (no markdown, no code fences):
{{
    "severity": "critical|high|medium|low",
    "fixability_score": <1-10, how likely code/automation could fix this>,
    "category": "bug|integration|automation|data|security|performance|ux|migration|other",
    "lead_score": <1-10, overall sales lead quality. 4+ if any real fixable problem exists>,
    "company_info": "<company size/industry guess, or 'unknown'>,
    "summary": "<one sentence: what is the problem>",
    "solution_approach": "<one sentence: how you'd fix it>"
}}

Scoring guide:
- 8-10: Clear business problem, urgent, company willing to pay, fixable with code
- 5-7: Real problem, likely fixable, some business value
- 3-4: Problem exists but vague, or might not need paid help
- 1-2: No real problem, already solved, or completely off-topic"""


class LeadClassifier:
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key)

    def classify(self, post):
        content = post.get("content", "")[:2500]
        if not content:
            content = post.get("title", "")

        prompt = CLASSIFY_PROMPT.format(
            source=post.get("source", "Unknown"),
            title=post.get("title", ""),
            content=content,
            author=post.get("author", ""),
        )

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.content[0].text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            return json.loads(text)
        except Exception as e:
            return {
                "severity": "unknown",
                "fixability_score": 0,
                "category": "unknown",
                "lead_score": 0,
                "company_info": "unknown",
                "summary": f"Classification failed: {e}",
                "solution_approach": "",
            }
