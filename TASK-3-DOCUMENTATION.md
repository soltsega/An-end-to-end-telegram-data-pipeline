# Task 3: Data Enrichment with Object Detection (YOLO)

## 📌 Overview
This task focuses on enriching the raw Telegram data by analyzing the images collected during the scraping process. We use an **Object Detection** pipeline (designed for **YOLOv8**) to identify objects in images and classify the content into business-relevant categories.

## 🎯 Goals
1.  **Scan** all images in the `data/raw/images/` directory.
2.  **Detect** objects (e.g., *bottle, person, cup*) and confidence scores.
3.  **Classify** images based on detected objects:
    *   **Promotional**: Contains a person and a product.
    *   **Product Display**: Contains a product but no person.
    *   **Lifestyle**: Contains a person but no product.
    *   **Other**: No relevant objects found.
4.  **Integrate** this data into the Data Warehouse for analytics.

## 🛠 Tech Stack
*   **Object Detection**: `ultralytics` (YOLOv8)
    *   *Note: Currently running in **Mock Mode** due to Python 3.14 incompatibility with `numpy`/`torch` on this environment.*
*   **Processing**: Python (Custom Script)
*   **Storage**: PostgreSQL (Raw Layer)
*   **Transformation**: dbt (Dimensional Modeling)

## 📂 Implementation Details

### 1. Detection Script (`src/yolo_detect.py`)
This script is the core of the enrichment layer.
*   **Function**: Iterates through the raw image directory.
*   **Refinement**: Extracts metadata (Channel Name, Message ID) from the file path.
*   **Inference**:
    *   **Real Mode (Planned)**: Loads `yolov8n.pt` and runs `model(image_path)`.
    *   **Mock Mode (Active)**: Simulates detection outputs deterministically to verify the pipeline structure without crashing the environment.
*   **Output**: Generates `data/processed/yolo_detections.csv`.

### 2. Database Loader (`scripts/load_yolo_to_postgres.py`)
A dedicated Python script to move the CSV data into the database.
*   **Schema**: `raw`
*   **Table**: `yolo_detections`
*   **Columns**: `image_path`, `channel_name`, `message_id`, `detected_objects`, `confidence_scores`, `classification`, `loaded_at`.

### 3. Data Warehouse Integration (`models/marts/fct_image_detections.sql`)
A **dbt model** that creates a Fact table for image analytics.
*   **Source**: `raw.yolo_detections`
*   **Joins**:
    *   Joins with `fct_messages` on `message_id` to link images to their original messages.
    *   Joins with `dim_channels` and `dim_dates` to enable slicing by channel and time.

## 📊 Deliverables
*   ✅ **Source Code**: `src/yolo_detect.py`
*   ✅ **Loader Script**: `scripts/load_yolo_to_postgres.py`
*   ✅ **Data**: `data/processed/yolo_detections.csv` (114 records successfully generated)
*   ✅ **dbt Model**: `models/marts/fct_image_detections.sql`

## ⚠️ Known Limitations (Environment)
The system is currently running Python **3.14**, which is not yet fully supported by the PyTorch ecosystem. As a result, the live `ultralytics` inference engine cannot run. The **Mock Implementation** ensures that the entire **Data Engineering Pipeline** (ETL flow, Database schemas, dbt models, and API endpoints) is fully implemented and verifiable, even without the ML inference model running locally.
