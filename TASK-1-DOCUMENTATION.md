# Task 1 Documentation: Data Scraping and Collection

## Overview
This document covers the implementation and results for the first phase of the Telegram Medical Warehouse project, which involved building a robust data scraping pipeline to populate a raw data lake.

## 1. Data Lake Structure
The raw data is stored in a partitioned directory structure to ensure scalability and ease of auditing.

- **Storage Location**: `data/raw/`
- **Messages**: `data/raw/telegram_messages/YYYY-MM-DD/{channel_name}.json`
- **Images**: `data/raw/images/{channel_name}/{message_id}.jpg`
- **Rationale**: Partitioning by date (`YYYY-MM-DD`) allows for incremental processing and prevents any single directory from becoming too bulky.

## 2. Technical Implementation Details
- **Library**: Built using `Telethon` (Asynchronous).
- **Flexibility**: Configurable message limits (`SCRAPE_LIMIT`) and channel lists via `src/config.py`.
- **Progress Tracking**: Uses `logs/checkpoints.json` to store the last successfully scraped `message_id`. This ensures no data is lost during interruptions and avoids duplicate scraping.
- **Error Handling**: Implemented exponential backoff for Telegram rate limiting (`FloodWaitError`).

## 3. Data Quality & Challenges
| Issue encountered | Resolution |
| :--- | :--- |
| **Telegram Rate Limiting** | Implemented automatic sleep/retry logic. |
| **Bulk Dependency Installation** | Large packages like `ultralytics` caused timeouts. Resolved by setting up a `venv` and installing essential Task 1 packages individually first. |
| **Session Management** | Configured `.gitignore` to protect sensitive `*.session` files while ensuring the scraper remains authenticated between runs. |

## 4. How to Run & Test
### Setup
```bash
python -m venv venv
.\venv\Scripts\activate
pip install telethon python-dotenv psycopg2-binary pytest
```

### Execution
```bash
.\venv\Scripts\python.exe src/scraper.py
```

### Verification
```bash
$env:PYTHONPATH="src"
.\venv\Scripts\python.exe -m pytest -o "asyncio_mode=auto" tests/test_scraper.py
```

## 5. Deliverables Status
- [x] Working Scraper: [scraper.py](file:///c:/Users/My%20Device/Desktop/Week-8-telegram-scraping-pipline/src/scraper.py)
- [x] Initial Data Lake: `data/raw/` populated with JSON and JPG files.
- [x] Progress Logs: [checkpoints.json](file:///c:/Users/My%20Device/Desktop/Week-8-telegram-scraping-pipline/logs/checkpoints.json)
- [x] Unit Tests: [test_scraper.py](file:///c:/Users/My%20Device/Desktop/Week-8-telegram-scraping-pipline/tests/test_scraper.py)

---
*Status: Task 1 Completed successfully on 2026-01-17.*
