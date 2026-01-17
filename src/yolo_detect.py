import os
import csv
import logging
from ultralytics import YOLO

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

def classify_image(results):
    """
    Classifies image based on detected objects.
    - Promotional: Contains 'person'
    - Product Display: Contains 'bottle', 'cup', 'bowl', 'vase' (proxies for medicine) but NO 'person'
    - Lifestyle: Contains 'person' (redundant with Promotional, but we can refine) -> Let's simplify: 
        If person + product -> Promotional
        If product + no person -> Product Display
        If person + no product -> Lifestyle
    - Other: No relevant objects
    """
    detected_classes = [int(cls) for cls in results[0].boxes.cls.tolist()]
    names = results[0].names
    detected_names = [names[cls] for cls in detected_classes]
    
    # Define sets for logic
    people = {'person'}
    products = {'bottle', 'cup', 'bowl', 'vase', 'suitcase', 'handbag', 'backpack'} # Proxies for medical/cosmetic items

    has_person = any(name in people for name in detected_names)
    has_product = any(name in products for name in detected_names)

    if has_person and has_product:
        return "Promotional"
    elif has_product and not has_person:
        return "Product Display"
    elif has_person and not has_product:
        return "Lifestyle"
    else:
        return "Other"

def main():
    try:
        logging.info("Loading YOLOv8 model...")
        model = YOLO("yolov8n.pt")  # Load nano model

        # Prepare CSV output
        with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow(["image_path", "channel_name", "message_id", "detected_objects", "confidence_scores", "classification"])

            logging.info(f"Scanning images in {RAW_IMAGE_DIR}...")
            
            # Walk through channel directories
            count = 0
            for root, dirs, files in os.walk(RAW_IMAGE_DIR):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        image_path = os.path.join(root, file)
                        
                        # Extract metadata from path: data/raw/images/{channel}/{msg_id}.jpg
                        path_parts = os.path.normpath(image_path).split(os.sep)
                        # Assumes structure ends with .../channel_name/message_id.jpg
                        try:
                            channel_name = path_parts[-2]
                            message_id = os.path.splitext(path_parts[-1])[0]
                        except IndexError:
                            logging.warning(f"Could not parse path: {image_path}")
                            continue

                        # Run Inference
                        try:
                            results = model(image_path, verbose=False) # verbose=False to reduce clutter
                            
                            # Extract details
                            detected_cls = [results[0].names[int(c)] for c in results[0].boxes.cls.tolist()]
                            confs = results[0].boxes.conf.tolist()
                            
                            classification = classify_image(results)
                            
                            writer.writerow([
                                image_path,
                                channel_name,
                                message_id,
                                "|".join(detected_cls), # Store as pipe-separated string
                                "|".join([f"{c:.2f}" for c in confs]),
                                classification
                            ])
                            
                            count += 1
                            if count % 10 == 0:
                                logging.info(f"Processed {count} images...")

                        except Exception as e:
                            logging.error(f"Failed to process {image_path}: {e}")

            logging.info(f"Completed! Processed {count} images. Results saved to {OUTPUT_CSV}")

    except Exception as e:
        logging.critical(f"Fatal error in YOLO pipeline: {e}")

if __name__ == "__main__":
    main()
