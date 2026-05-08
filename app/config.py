import json
import os

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".forum_parser")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "anthropic_api_key": "",
    "reddit_client_id": "",
    "reddit_client_secret": "",
    "reddit_user_agent": "ForumParser/1.0",
    "github_token": "",
    "scrape_sources": {
        "reddit": True,
        "github": True,
        "hackernews": True,
        "microsoft": True,
    },
    "reddit_subreddits": [
        "smallbusiness", "SaaS", "Entrepreneur", "sysadmin",
        "webdev", "devops", "ITManagers", "msp",
    ],
    "github_queries": [
        "bug help wanted", "integration issue", "breaking change",
    ],
    "keywords": [
        "frustrated", "broken", "doesn't work", "help needed",
        "critical bug", "losing money", "deadline", "urgent",
        "switching from", "looking for alternative", "any solution",
    ],
    "min_lead_score": 5.0,
    "max_results_per_source": 50,
}


class Config:
    def __init__(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.data = self._load()

    def _load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                saved = json.load(f)
                merged = DEFAULT_CONFIG.copy()
                merged.update(saved)
                return merged
        return DEFAULT_CONFIG.copy()

    def save(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
