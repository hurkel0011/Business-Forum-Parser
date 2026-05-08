import json
import os
from pathlib import Path

from dotenv import load_dotenv, set_key

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".forum_parser")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

ENV_KEY_MAP = {
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "GITHUB_TOKEN": "github_token",
    "MIN_LEAD_SCORE": "min_lead_score",
    "MAX_RESULTS_PER_SOURCE": "max_results_per_source",
}

CONFIG_TO_ENV = {v: k for k, v in ENV_KEY_MAP.items()}

DEFAULT_CONFIG = {
    "anthropic_api_key": "",
    "github_token": "",
    "scrape_sources": {
        "websearch": True,
        "github": True,
        "hackernews": True,
        "microsoft": True,
        "stackoverflow": True,
    },
    "keywords": [
        "frustrated", "broken", "doesn't work", "help needed",
        "critical bug", "losing money", "deadline", "urgent",
        "switching from", "looking for alternative", "any solution",
        "integration issue", "workflow broken", "production down",
        "need automation", "manual process", "data migration",
    ],
    "min_lead_score": 3.0,
    "max_results_per_source": 30,
}

NUMERIC_KEYS = {"min_lead_score", "max_results_per_source"}


class Config:
    def __init__(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        load_dotenv(ENV_FILE)
        self.data = self._load()

    def _load(self):
        merged = DEFAULT_CONFIG.copy()

        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                merged.update(json.load(f))

        for env_var, config_key in ENV_KEY_MAP.items():
            val = os.environ.get(env_var, "")
            if val:
                if config_key in NUMERIC_KEYS:
                    try:
                        val = float(val)
                    except ValueError:
                        continue
                merged[config_key] = val

        return merged

    def save(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

        if ENV_FILE.exists():
            for config_key, env_var in CONFIG_TO_ENV.items():
                val = self.data.get(config_key, "")
                if val is not None:
                    set_key(str(ENV_FILE), env_var, str(val))

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
