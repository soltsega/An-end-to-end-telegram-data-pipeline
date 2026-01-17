# Task 2 Documentation: Data Modeling and Transformation

## Overview
This document covers the implementation of the Data Warehouse layer using **PostgreSQL** and **dbt (Data Build Tool)**. The goal was to transform raw, messy JSON data into a clean, structured Star Schema optimized for analytics.

## 1. Architecture

### Tech Stack
- **Database**: PostgreSQL 15 (Dockerized)
- **Transformation**: dbt Core 1.8.2
- **Orchestration**: Docker Compose (running dbt in a container for stability)

### Schemas
- `raw`: Landing zone for raw data (loaded from JSON).
- `staging`: Views that clean, type-cast, and standardize raw data (`stg_telegram_messages`).
- `marts`: The business-facing Star Schema (`dim_channels`, `dim_dates`, `fct_messages`).

## 2. Dimensional Model (Star Schema)

### Fact Table
- **`fct_messages`**: Central table containing one row per message.
  - **Metrics**: `message_length`, `view_count`, `forward_count`.
  - **Keys**: `message_id`, `channel_key` (FK), `message_date` (FK).

### Dimension Tables
- **`dim_channels`**: Channel metadata and aggregated stats (e.g., `total_posts`, `avg_views`).
- **`dim_dates`**: A comprehensive date spine generated using `dbt_utils` to enable gapless time-series analysis.

## 3. Data Quality & Testing
We implemented a robust testing suite to ensure data trust:

| Test Type | Description | Count |
| :--- | :--- | :--- |
| **Schema Tests** | `unique`, `not_null` constraints on primary keys and `relationships` (FKs). | 10 |
| **Business Rules** | `assert_no_future_messages`: Ensures no posts have future dates. | 1 |
| **Business Rules** | `assert_positive_views`: Ensures view counts are non-negative. | 1 |
| **Total Tests** | **12 Passing Tests** | ✅ |

## 4. Execution Guide

### Load Raw Data
```bash
# Ensure your database credentials are in .env
.\venv\Scripts\python.exe scripts/load_to_postgres.py
```

### Run dbt Transformations
We use Docker to run dbt to avoid Python version conflicts.

```bash
# Build the models
docker-compose run dbt run

# Run the tests
docker-compose run dbt test

# Generate documentation
docker-compose run dbt docs generate
```

---
*Status: Task 2 Completed successfully on 2026-01-17.*
