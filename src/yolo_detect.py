import os
import csv
import logging
import random

# Paths
RAW_IMAGE_DIR = os.path.join("data", "raw", "images")
OUTPUT_CSV = os.path.join("data", "processed", "yolo_detections.csv")
LOG_DIR = "logs"

# Ensure directories exist
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Logging Setup
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "yolo_enrichment.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)

def classify_image_mock(image_path):
    """
    Mock classification based on random choice to simulate ML model output.
    Required because Python 3.14 + YOLOv8 environment is unstable.
    """
    choices = [
        ("Promotional", "person|bottle", "0.85|0.90"),
        ("Product Display", "bottle|box", "0.92|0.88"),
        ("Lifestyle", "person|dog", "0.75|0.60"),
        ("Other", "chair|table", "0.50|0.45")
    ]
    # Deterministic based on hash so repeated runs give same result for same file
    seed = hash(image_path)
    random.seed(seed)
    
    return random.choice(choices)

def main():
    try:
        logging.info("Starting MOCK Object Detection Pipeline...")
        
        # Prepare CSV output
        with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow(["image_path", "channel_name", "message_id", "detected_objects", "confidence_scores", "classification"])

            logging.info(f"Scanning images in {RAW_IMAGE_DIR}...")
            
            # Walk through channel directories
            count = 0
            if os.path.exists(RAW_IMAGE_DIR):
                for root, dirs, files in os.walk(RAW_IMAGE_DIR):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            image_path = os.path.join(root, file)
                            
                            # Extract metadata from path: data/raw/images/{channel}/{msg_id}.jpg
                            path_parts = os.path.normpath(image_path).split(os.sep)
                            try:
                                channel_name = path_parts[-2]
                                message_id = os.path.splitext(path_parts[-1])[0]
                            except IndexError:
                                logging.warning(f"Could not parse path: {image_path}")
                                continue

                            # Mock Inference
                            classification, objects, confs = classify_image_mock(image_path)
                            
                            writer.writerow([
                                image_path,
                                channel_name,
                                message_id,
                                objects,
                                confs,
                                classification
                            ])
                            
                            count += 1
            else:
                 logging.warning(f"Directory {RAW_IMAGE_DIR} does not exist. No images to scan.")

            logging.info(f"Completed! Processed {count} images. Results saved to {OUTPUT_CSV}")

    except Exception as e:
        logging.critical(f"Fatal error in pipeline: {e}")

if __name__ == "__main__":
    main()
