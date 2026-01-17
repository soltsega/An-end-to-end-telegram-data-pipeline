# Task 4: Analytical API Development

## 📌 Overview
This task focuses on exposing the data stored in our Data Warehouse (PostgreSQL) via a RESTful API. The API serves as the bridge between our data engineering pipeline and potential frontend applications or dashboards.

## 🎯 Goals
1.  **Framework Setup**: Initialize a FastAPI project structure.
2.  **Database Connection**: Connect to the existing PostgreSQL warehouse using SQLAlchemy.
3.  **Data Validation**: Use Pydantic schemas for request/response standardization.
4.  **Endpoints**: Implement 4 specific analytical endpoints:
    *   `GET /reports/top-products`: Trending keywords.
    *   `GET /channels/{name}/activity`: Posting frequency.
    *   `GET /search/messages`: Full-text search.
    *   `GET /reports/visual-content`: Image classification stats (from Task 3).

## 🛠 Tech Stack
*   **Framework**: `FastAPI` (High performance, easy documentation)
*   **Server**: `Uvicorn` (ASGI server)
*   **ORM**: `SQLAlchemy` (Database interaction)
*   **Validation**: `Pydantic` (Data schemas)
*   **Database**: PostgreSQL (Driver: `psycopg2-binary`)

## 📂 Implementation Details

### 1. Project Structure (`api/`)
*   `main.py`: The entry point. Defines the `app` object and all route handlers.
*   `database.py`: Handles the DB connection pool (`SessionLocal`) and session lifecycle management.
*   `schemas.py`: Defines the shape of JSON responses (e.g., `MessageBase`, `TopProductResponse`).

### 2. Endpoints Implemented

#### A. Top Products Report
*   **Route**: `GET /api/reports/top-products`
*   **Logic**: Performs a SQL aggregation (COUNT) on keywords found in the `fct_messages` table.
*   **Schema**: `[{ "product_name": "string", "mention_count": int }]`

#### B. Channel Activity
*   **Route**: `GET /api/channels/{channel_name}/activity`
*   **Logic**: Joins `fct_messages` -> `dim_channels` -> `dim_dates` to provide a daily time-series of message volume and views.
*   **Schema**: `[{ "date": "YYYY-MM-DD", "message_count": int, "total_views": int }]`

#### C. Content Search
*   **Route**: `GET /api/search/messages`
*   **Logic**: Uses PostgreSQL `ILIKE` for case-insensitive keyword search across message history.
*   **Schema**: List of `Message` objects including metadata (views, forwards).

#### D. Visual Content Stats (Integration with Task 3)
*   **Route**: `GET /api/reports/visual-content`
*   **Logic**: Aggregates data from the `fct_image_detections` table (created in Task 3) to show the distribution of image classes (Promotional vs Lifestyle).
*   **Schema**: `[{ "image_category": "string", "count": int, "avg_confidence": float }]`

## 📊 Deliverables Verified
*   ✅ **Codebase**: `api/` directory is complete.
*   ✅ **Connection**: `database.py` correctly reads usage from `.env`.
*   ✅ **Validation**: `schemas.py` ensures strict typing.
*   ✅ **API Docs**: Swagger UI is automatically available at `/docs` when running the server.

## 🚀 Execution Guide
To run the API locally:
```bash
uvicorn api.main:app --reload
```
Then visit: `http://127.0.0.1:8000/docs`
