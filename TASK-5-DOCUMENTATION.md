# Task 5: Pipeline Orchestration with Dagster

## 📌 Overview
This task automates the end-to-end data pipeline using **Dagster**. Instead of running individual scripts manually, Dagster manages the execution order, dependencies, and error handling for the entire workflow.

## 🎯 Goals
1.  **Wrap Scripts**: Encapsulate existing Python scripts (`scraper.py`, `load_to_postgres.py`, etc.) into Dagster **Assets**.
2.  **Define Dependencies**: Ensure the pipeline runs in the correct order:
    *   Scrape -> Load Raw -> Enrich (YOLO) -> Load Enrichment.
3.  **Schedule**: Create a job that can be triggered daily.

## 🛠 Tech Stack
*   **Orchestrator**: `Dagster`
*   **Interface**: `Dagster UI` (Webserver)
*   **Language**: Python 3.10+

## 📂 Implementation Details

### 1. Project Structure (`orchestration/`)
The orchestration logic is isolated from the application code:
*   `assets.py`: Defines the software-defined assets.
*   `jobs.py`: Groups assets into executable jobs.
*   `definitions.py`: The main entry point for the Dagster webserver.

### 2. Assets Defined
We created four key assets:

| Asset Name | Underlying Script | Description |
| :--- | :--- | :--- |
| `scrape_telegram` | `src/scraper.py` | Scrapes messages and images to the local Data Lake. |
| `load_raw_data` | `scripts/load_to_postgres.py` | Loads raw JSON files into the PostgreSQL `raw` schema. |
| `enrich_data_yolo` | `src/yolo_detect.py` | Runs Object Detection (Mock) on images and generates a CSV. |
| `(Implicit Load)` | `scripts/load_yolo_to_postgres.py` | Called within `enrich_data_yolo` to load CSV to DB. |

### 3. The Pipeline Job (`daily_pipeline_job`)
This job materializes all assets in the dependency order:
1.  **Start**: `scrape_telegram`
2.  **Wait for Scrape**: `load_raw_data`
3.  **Wait for Load**: `enrich_data_yolo`

## 🚀 Execution Guide
To run the pipeline:

1.  **Start the UI**:
    ```bash
    dagster dev -f orchestration/definitions.py
    ```
2.  **Trigger Job**:
    *   Open `http://localhost:3000`
    *   Go to "Overview" -> "Jobs" -> `daily_pipeline_job`
    *   Click "Launch Pad" -> "Launch Run"

## ✅ Deliverables
*   `orchestration/assets.py`
*   `orchestration/definitions.py`
*   `orchestration/jobs.py`
