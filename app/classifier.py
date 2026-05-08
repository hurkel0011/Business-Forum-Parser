import json
from anthropic import Anthropic


CLASSIFY_PROMPT = """Analyze this forum post and classify it as a potential business lead.
Someone could fix this problem with code/automation and sell the solution.

Post Source: {source}
Post Title: {title}
Post Content: {content}
Author: {author}

Respond with ONLY valid JSON (no markdown, no code fences):
{{
    "severity": "critical|high|medium|low",
    "fixability_score": <1-10, how likely a developer could fix this with code>,
    "category": "bug|integration|automation|data|security|performance|ux|other",
    "lead_score": <1-10, overall quality as a sales lead>,
    "company_info": "<estimated company size/industry if detectable, otherwise unknown>",
    "summary": "<one sentence summary of the problem>",
    "solution_approach": "<brief description of how you would fix this>"
}}"""


class LeadClassifier:
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key)

    def classify(self, post):
        prompt = CLASSIFY_PROMPT.format(
            source=post.get("source", "Unknown"),
            title=post.get("title", ""),
            content=post.get("content", "")[:1500],
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
