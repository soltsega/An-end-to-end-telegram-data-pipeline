# Medical Telegram Warehouse

An end-to-end data pipeline for Telegram, leveraging dbt for transformation, Dagster for orchestration, and YOLOv8 for data enrichment.

## Project Structure

- `data/`: Raw and processed data storage.
- `src/`: Source code for scrapers and processing scripts.
- `api/`: FastAPI application for exposing data.
- `medical_warehouse/`: dbt project for data transformation.
- `notebooks/`: Jupyter notebooks for exploratory data analysis.
- `tests/`: Unit and integration tests.
- `scripts/`: Utility scripts.
- `dagster/`: Orchestration logic.

## Setup

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure `.env` file with your credentials.
