import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from repository root (if present)
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

def getenv(key, default=None):
    val = os.getenv(key)
    return val if val is not None else default

# Google / Gemini
GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")
DEFAULT_MODEL = getenv("DEFAULT_MODEL", "gemini-1.5-flash")

# OpenAI (if used)
OPENAI_API_KEY = getenv("OPENAI_API_KEY")

# Gmail / Email
GMAIL_ADDRESS = getenv("GMAIL_ADDRESS")
GMAIL_SMTP_SERVER = getenv("GMAIL_SMTP_SERVER", "smtp.gmail.com")
GMAIL_SMTP_PORT = int(getenv("GMAIL_SMTP_PORT", 587))

# Image hosting
IMGBB_API_KEY = getenv("IMGBB_API_KEY")

# Notifications
TELEGRAM_CHAT_ID = getenv("TELEGRAM_CHAT_ID")

# Social platforms (placeholders)
TWITTER_BEARER_TOKEN = getenv("TWITTER_BEARER_TOKEN")
FACEBOOK_ACCESS_TOKEN = getenv("FACEBOOK_ACCESS_TOKEN")
LINKEDIN_ACCESS_TOKEN = getenv("LINKEDIN_ACCESS_TOKEN")

# App defaults
OUTPUT_DIR = getenv("OUTPUT_DIR", str(ROOT / "outputs"))
YOUTUBE_URL_DEFAULT = getenv("YOUTUBE_URL", "")

def as_dict():
    return {
        "GOOGLE_API_KEY": GOOGLE_API_KEY,
        "DEFAULT_MODEL": DEFAULT_MODEL,
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "GMAIL_ADDRESS": GMAIL_ADDRESS,
        "IMGBB_API_KEY": IMGBB_API_KEY,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
        "TWITTER_BEARER_TOKEN": TWITTER_BEARER_TOKEN,
        "FACEBOOK_ACCESS_TOKEN": FACEBOOK_ACCESS_TOKEN,
        "LINKEDIN_ACCESS_TOKEN": LINKEDIN_ACCESS_TOKEN,
        "OUTPUT_DIR": OUTPUT_DIR,
        "YOUTUBE_URL_DEFAULT": YOUTUBE_URL_DEFAULT,
    }
