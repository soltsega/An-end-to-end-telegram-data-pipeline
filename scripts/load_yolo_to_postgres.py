import os
import csv
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# DB Config
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

CSV_PATH = os.path.join("data", "processed", "yolo_detections.csv")

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def setup_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS raw.yolo_detections (
            image_path TEXT,
            channel_name TEXT,
            message_id INTEGER,
            detected_objects TEXT,
            confidence_scores TEXT,
            classification TEXT,
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    # Optional: Truncate to avoid duplicates on re-run, or handle upsert. 
    # For now, let's truncate for simplicity in this pipeline step.
    cursor.execute("TRUNCATE TABLE raw.yolo_detections;")

def load_csv():
    if not os.path.exists(CSV_PATH):
        print(f"File not found: {CSV_PATH}. Run src/yolo_detect.py first.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        setup_table(cursor)
        
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader) # Skip header
            
            data = []
            for row in reader:
                # Row structure: [path, channel, msg_id, objects, confs, class]
                data.append((
                    row[0], # image_path
                    row[1], # channel_name
                    int(row[2]), # message_id
                    row[3], # detected_objects
                    row[4], # confidence_scores
                    row[5]  # classification
                ))
            
            if data:
                insert_query = """
                    INSERT INTO raw.yolo_detections 
                    (image_path, channel_name, message_id, detected_objects, confidence_scores, classification)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.executemany(insert_query, data)
                conn.commit()
                print(f"Successfully loaded {len(data)} detection records to raw.yolo_detections.")
            else:
                print("CSV is empty, nothing loaded.")

    except Exception as e:
        conn.rollback()
        print(f"Error loading YOLO data: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    load_csv()
