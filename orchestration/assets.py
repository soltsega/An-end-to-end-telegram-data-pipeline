import os
import sys
from dagster import asset, Output, MetadataValue

# Add the project root to the python path so we can import src/scripts
sys.path.append(os.getcwd())

from src.scraper import TelegramScraper
from scripts.load_to_postgres import load_json_to_postgres
from src.yolo_detect import main as yolo_main
from scripts.load_yolo_to_postgres import load_csv as load_yolo_csv

@asset
def scrape_telegram(context):
    """
    Scrapes Telegram channels and saves JSON/Images to data lake.
    """
    context.log.info("Starting Telegram Scraper...")
    # NOTE: In a real production run, you might want to call the async main loop properly. 
    # For now, we assume the scraper class usage or a simplified sync wrapper.
    # Given the scraper is async, we might need a subprocess call or asyncio.run if not handled by the script.
    
    # Running via subprocess to ensure clean async loop handling and environment isolation if needed
    import subprocess
    result = subprocess.run(["python", "src/scraper.py"], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Scraper failed: {result.stderr}")
    
    context.log.info(result.stdout)
    return Output(None, metadata={"status": "Scraping complete"})

@asset(deps=[scrape_telegram])
def load_raw_data(context):
    """
    Loads raw JSON data from data lake to PostgreSQL.
    """
    context.log.info("Loading JSON to Postgres...")
    load_json_to_postgres()
    return Output(None, metadata={"status": "Raw data loaded"})

@asset(deps=[load_raw_data])
def enrich_data_yolo(context):
    """
    Runs YOLO detection on images and loads results to Postgres.
    """
    context.log.info("Running YOLO Enrichment...")
    yolo_main() # Runs detection -> saves CSV
    
    context.log.info("Loading YOLO results to Postgres...")
    load_yolo_csv() # Loads CSV -> Postgres
    
    return Output(None, metadata={"status": "Enrichment complete"})
