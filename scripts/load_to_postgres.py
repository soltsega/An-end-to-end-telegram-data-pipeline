import os
import json
import psycopg2
from psycopg2 import sql
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

RAW_DATA_PATH = "data/raw/telegram_messages"

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def setup_raw_schema(cursor):
    """Creates the raw schema and the initial landing table."""
    cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.telegram_messages (
            id SERIAL PRIMARY KEY,
            message_id INTEGER,
            channel_name TEXT,
            message_date TIMESTAMP,
            message_text TEXT,
            has_media BOOLEAN,
            image_path TEXT,
            views INTEGER,
            forwards INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

def load_json_to_postgres():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        setup_raw_schema(cursor)
        
        # Iterate through date folders in data/raw/telegram_messages
        for date_folder in os.listdir(RAW_DATA_PATH):
            folder_path = os.path.join(RAW_DATA_PATH, date_folder)
            if not os.path.isdir(folder_path):
                continue
                
            for json_file in os.listdir(folder_path):
                if not json_file.endswith(".json"):
                    continue
                    
                file_path = os.path.join(folder_path, json_file)
                with open(file_path, "r", encoding="utf-8") as f:
                    messages = json.load(f)
                    
                for msg in messages:
                    # Check if message already exists to avoid duplicates
                    cursor.execute("""
                        SELECT 1 FROM raw.telegram_messages 
                        WHERE message_id = %s AND channel_name = %s
                    """, (msg['message_id'], msg['channel_name']))
                    
                    if cursor.fetchone():
                        continue
                        
                    insert_query = """
                        INSERT INTO raw.telegram_messages (
                            message_id, channel_name, message_date, 
                            message_text, has_media, image_path, views, forwards
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        msg['message_id'],
                        msg['channel_name'],
                        msg['message_date'],
                        msg['message_text'],
                        msg['has_media'],
                        msg['image_path'],
                        msg['views'],
                        msg['forwards']
                    ))
                
                print(f"Loaded {len(messages)} messages from {json_file}")
        
        conn.commit()
        print("Data loading completed successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error loading data: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if os.path.exists(RAW_DATA_PATH):
        load_json_to_postgres()
    else:
        print(f"Path {RAW_DATA_PATH} does not exist. Run the scraper first.")
