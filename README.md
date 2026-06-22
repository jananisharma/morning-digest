# Morning Digest Agent

An AI-powered personal news briefing agent built with Python and Claude.

## What it does
Fetches RSS feeds across AI/Tech, Music Industry, Biotech & Wellness, and Consumer Markets every day, summarizes the top stories using Claude, generates a personalized strategic move for each story, and emails the digest with a witty subject line.

## Built with
- Python 3.14
- Anthropic Claude API
- feedparser
- smtplib
- launchd (Mac scheduler)

## Setup
1. Clone the repo
2. Create a `.env` file with your API keys (see `.env.example`)
3. Install dependencies: `pip install anthropic feedparser python-dotenv`
4. Run: `python3 morning_digest.py`
