import os
from dotenv import load_dotenv

load_dotenv()

TG_API_ID = os.getenv("TG_API_ID")
TG_API_HASH = os.getenv("TG_API_HASH")
TG_PHONE = os.getenv("TG_PHONE")

CHANNELS = [
    "@lobelia4cosmetics",
    "@tikvahpharma",
    "@CheMed123"
]

SCRAPE_LIMIT = 50  # Number of messages per channel per run
RAW_DATA_PATH = "data/raw/telegram_messages"
IMAGE_DATA_PATH = "data/raw/images"
LOG_DIR = "logs"
