import os
import json
import logging
import asyncio
from datetime import datetime
from telethon import TelegramClient, errors
from config import TG_API_ID, TG_API_HASH, TG_PHONE, CHANNELS, RAW_DATA_PATH, IMAGE_DATA_PATH, LOG_DIR, SCRAPE_LIMIT

# Set up logging
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "scraper.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)

class TelegramScraper:
    def __init__(self):
        self.client = TelegramClient('scraper_session', TG_API_ID, TG_API_HASH)
        self.checkpoints_file = os.path.join(LOG_DIR, "checkpoints.json")
        self.checkpoints = self.load_checkpoints()

    def load_checkpoints(self):
        if os.path.exists(self.checkpoints_file):
            with open(self.checkpoints_file, 'r') as f:
                return json.load(f)
        return {}

    def save_checkpoints(self):
        with open(self.checkpoints_file, 'w') as f:
            json.dump(self.checkpoints, f, indent=4)

    async def scrape_channel(self, channel_username, limit=SCRAPE_LIMIT):
        logging.info(f"Starting scrape for {channel_username}...")
        try:
            entity = await self.client.get_entity(channel_username)
            channel_name = entity.title
            
            # Use checkpoint to resume
            offset_id = self.checkpoints.get(channel_username, 0)
            
            messages = []
            count = 0
            
            # Sort directory by date
            today = datetime.now().strftime("%Y-%m-%d")
            store_path = os.path.join(RAW_DATA_PATH, today)
            os.makedirs(store_path, exist_ok=True)
            
            img_store_path = os.path.join(IMAGE_DATA_PATH, channel_username.replace("@", ""))
            os.makedirs(img_store_path, exist_ok=True)

            async for message in self.client.iter_messages(entity, limit=limit, min_id=offset_id):
                msg_data = {
                    "message_id": message.id,
                    "channel_name": channel_username,
                    "message_date": str(message.date),
                    "message_text": message.text or "",
                    "has_media": message.photo is not None,
                    "views": message.views or 0,
                    "forwards": message.forwards or 0,
                    "image_path": None
                }

                if message.photo:
                    image_filename = f"{message.id}.jpg"
                    image_path = os.path.join(img_store_path, image_filename)
                    await self.client.download_media(message.photo, file=image_path)
                    msg_data["image_path"] = image_path

                messages.append(msg_data)
                count += 1
                
                # Update checkpoint with the latest ID seen
                if message.id > self.checkpoints.get(channel_username, 0):
                    self.checkpoints[channel_username] = message.id

            if messages:
                json_filename = f"{channel_username.replace('@', '')}.json"
                with open(os.path.join(store_path, json_filename), "w", encoding="utf-8") as f:
                    json.dump(messages, f, ensure_ascii=False, indent=4)
                
                self.save_checkpoints()
                logging.info(f"Successfully scraped {count} messages from {channel_username}")
            else:
                logging.info(f"No new messages found for {channel_username}")

        except errors.FloodWaitError as e:
            logging.error(f"Rate limited. Need to wait for {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            logging.error(f"Error scraping {channel_username}: {str(e)}")

    async def run(self):
        await self.client.start(phone=TG_PHONE)
        tasks = [self.scrape_channel(channel) for channel in CHANNELS]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    scraper = TelegramScraper()
    asyncio.run(scraper.run())
