# Business Forum Parser v1.0

Desktop app that scrapes business forums for complaints and issues, classifies them with Claude AI, and presents actionable leads you can sell as solutions.

## Features

- **Multi-source scraping** — Reddit, GitHub Issues, Hacker News, Microsoft Tech Community
- **AI-powered classification** — Claude analyzes severity, fixability, and lead quality
- **Lead management** — Filter, sort, track status, and export to CSV
- **Dashboard** — Stats overview with lead scoring
- **Dark theme** — Modern desktop UI built with CustomTkinter

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## API Keys Required

Configure in the Settings tab:

- **Anthropic API Key** — for Claude-based post classification
- **Reddit API credentials** — create an app at https://www.reddit.com/prefs/apps
- **GitHub Token** (optional) — increases rate limits for GitHub Issues scraping

## How It Works

1. Open the app and go to **Settings** — enter your API keys
2. Go to **Scrape Forums** — select sources, optionally enter a search query
3. Click **Start Scraping** — the app pulls posts and classifies each one with Claude
4. Go to **Leads** — browse scored leads, filter by severity/source/status
5. Click a lead to see details, open the original URL, or export to CSV

## Lead Scoring

Each post is scored 1-10 on:
- **Severity** — how critical is the problem?
- **Fixability** — can a developer realistically solve this?
- **Lead Score** — overall quality as a sales opportunity

## Tech Stack

- Python 3.10+
- CustomTkinter (desktop GUI)
- Anthropic SDK (Claude API)
- PRAW (Reddit API)
- Requests + BeautifulSoup (web scraping)
- SQLite (local database)
