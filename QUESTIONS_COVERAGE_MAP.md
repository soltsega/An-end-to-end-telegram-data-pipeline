# Questions Coverage Map - Task 1-2 Interim Report

This document maps the required submission questions to their answers in the `INTERIM_REPORT_TASK1-2.md`.

---

## ✅ Business Alignment

### Question 1: How does the data pipeline support Kara Solutions' mission to generate actionable insights on Ethiopian medical businesses?

**Answered in**: 
- **Section 1.1** (Page 2): "Kara Solutions' Strategic Goal"
- **Section 1.3** (Pages 2-3): "How Tasks 1 & 2 Address These Objectives"

**Key Points Covered**:
- Kara Solutions seeks "data-driven competitive advantage in Ethiopian medical market"
- Telegram is the "primary communication and commerce platform" → Makes it rich data source
- Pipeline transforms "unstructured Telegram content into actionable business intelligence"
- Enables answering 3 strategic questions: product trends, pricing intelligence, engagement patterns

**Direct Quote**:
> "Kara Solutions aims to establish a data-driven competitive advantage in the Ethiopian medical and pharmaceutical market by transforming unstructured Telegram content into actionable business intelligence."

---

### Question 2: How do Tasks 1 and 2 contribute to solving the business questions?

**Answered in**: **Section 1.3** (Pages 2-3): "How Tasks 1 & 2 Address These Objectives"

**Task 1 Contribution**:
- "Capturing raw market signals" from 3 channels representing different segments
- "Preserving both text and visual content" for multi-modal analysis
- "Enabling historical and real-time analysis" through checkpoint-based scraping

**Task 2 Contribution**:
- "Structuring unstructured content into dimensional model optimized for analytics"
- `dim_channels`: "Enables competitive benchmarking"
- `dim_dates`: "Powers trend analysis"
- `fct_messages`: Central fact table with engagement metrics

**Integration for Business Questions**:
| Business Question | How Pipeline Answers It |
|:------------------|:------------------------|
| Product Trends | `fct_messages.message_content` enables keyword extraction; `dim_dates` shows temporal patterns |
| Pricing Intelligence | Cross-channel analysis via `dim_channels` aggregations |
| Engagement Patterns | `view_count`, `forward_count` metrics joined with image metadata (future Task 3) |

---

## ✅ Data Scraping and Collection (Task 1)

### Question 3: Which Telegram channels were scraped and what specific fields were collected?

**Answered in**: 
- **Channels**: Section 1.3 (Page 2) + Section 2.1.4 (Page 5)
- **Fields**: Section 2.1.1 (Page 3) + Section 2.2.5 (Page 7)

**Channels Scraped**:
1. **CheMed123**: General pharmaceuticals (50 messages, 47 images)
2. **Lobelia4cosmetics**: Cosmetics and wellness products (50 messages, 51 images)
3. **TikvahPharma**: Specialized medical supplies (50 messages, 16 images)

**Total**: 150 messages, 114 images

**Fields Collected** (per message):
```python
{
  "message_id": INTEGER,
  "channel_name": TEXT,
  "message_date": TIMESTAMP,
  "message_text": TEXT,
  "has_media": BOOLEAN,
  "views": INTEGER,
  "forwards": INTEGER,
  "image_path": TEXT (nullable)
}
```

**Source in Report**: Section 2.1.1 states "Dual Output Streams: Structured JSON metadata (message_id, date, text, views, forwards)"

**Example from Actual Data** (shown in checkpoint exploration):
```json
{
  "message_id": 97,
  "channel_name": "@CheMed123",
  "message_date": "2023-02-10 12:23:06+00:00",
  "message_text": "⚠️Notice! Dear esteemed customers...",
  "has_media": true,
  "views": 1290,
  "forwards": 1,
  "image_path": "data/raw/images\\CheMed123\\97.jpg"
}
```

---

### Question 4: How is the raw data stored (JSON files, image directory structure)?

**Answered in**: **Section 2.1.2** (Page 3): "Data Lake Structure"

**Storage Organization**:
```
data/raw/
├── telegram_messages/
│   └── 2026-01-17/           # DATE-PARTITIONED
│       ├── CheMed123.json    # 50 messages
│       ├── lobelia4cosmetics.json  # 50 messages
│       └── tikvahpharma.json       # 50 messages
└── images/
    ├── CheMed123/            # 47 images
    ├── lobelia4cosmetics/    # 51 images
    └── tikvahpharma/         # 16 images
```

**Rationale Explained**:
- **Date partitioning** (`YYYY-MM-DD` folders) enables:
  - Efficient incremental backfills
  - Simplified data lifecycle management
  - Fast lookups when loading to database

**Image Naming Convention**: `{message_id}.jpg` (e.g., `97.jpg` for message ID 97)

---

### Question 5: What measures were taken for logging and error handling?

**Answered in**: **Section 2.1.3** (Pages 4-5): "Data Quality Handling and Error Resilience"

**Three Key Strategies Detailed**:

**1. Rate Limit Management**:
- Handles `FloodWaitError` exceptions
- **Code snippet shown**:
  ```python
  except errors.FloodWaitError as e:
      logging.error(f"Rate limited. Need to wait for {e.seconds} seconds")
      await asyncio.sleep(e.seconds)
  ```
- Automatically pauses and resumes → Zero data loss

**2. Checkpoint-Based Resumption**:
- Maintains `logs/checkpoints.json` tracking highest `message_id` per channel
- **Example checkpoint shown**:
  ```json
  {
    "@CheMed123": 97,
    "@lobelia4cosmetics": 22908,
    "@tikvahpharma": 188977
  }
  ```
- Benefits: Interruption recovery, deduplication, audit trail

**3. Comprehensive Logging**:
- All events logged to `logs/scraper.log`
- **INFO**: Successful scrapes, message counts
- **ERROR**: Rate limits, network failures, authentication issues
- Used for debugging and production monitoring

---

## ✅ Data Loading and Transformation (Task 2)

### Question 6: How is the raw data loaded into PostgreSQL and what initial quality checks have been applied?

**Answered in**: **Section 2.2.5** (Page 7): "Data Loading Process"

**Loading Process** (`scripts/load_to_postgres.py`):

**Key Features**:
1. **Idempotent Loading**:
   - Checks for existing `(message_id, channel_name)` combinations before inserting
   - Prevents duplicates during re-runs
   
2. **Error Handling**:
   - Uses `try-except` blocks with transaction rollback on failure
   - Ensures atomic operations (all or nothing)

3. **Schema Auto-Creation**:
   - Automatically creates `raw` schema and `telegram_messages` table if missing
   - Reduces manual setup steps

**Quality Checks Applied**:
- **Deduplication**: Lines 68-75 of `load_to_postgres.py` check for existing records
- **Type Validation**: PostgreSQL schema enforces data types (INTEGER for IDs, TIMESTAMP for dates)
- **NULL Handling**: Schema allows NULLs for optional fields (`image_path`, `forwards`)

**Additional Quality Checks in Section 2.2.4**:
- **12 dbt tests** ensuring data integrity (100% pass rate)
- Schema tests: `unique`, `not_null`, `relationships`
- Custom tests: `assert_no_future_messages`, `assert_positive_views`

---

### Question 7: How are the dbt staging models structured to clean/standardize the data?

**Answered in**: **Section 2.2.3** (Pages 6-7): "Staging Layer: Data Cleaning"

**Transformations in `stg_telegram_messages`**:

**1. Type Casting**:
```sql
CAST(message_date AS TIMESTAMP) AS message_date_ts,
CAST(views AS INTEGER) AS view_count,
CAST(forwards AS INTEGER) AS forward_count
```

**2. Handling Missing Data**:
- NULL `views` → 0 (channels sometimes disable view counts)
- NULL `message_text` → empty string (image-only posts)

**3. Deduplication**:
- Uses `DISTINCT ON (message_id, channel_name)` to handle accidental duplicates

**4. Derived Fields**:
- `message_length`: `LENGTH(message_text)` for content analysis
- `has_media_flag`: Converts boolean to 1/0 for analytics

**Purpose**: Transform raw, messy JSON into clean, typed, analytics-ready dataset before loading to marts layer.

---

### Question 8: How does the star schema design support analytical needs?

**Answered in**: **Section 2.2.2** (Pages 5-6): "Star Schema Design"

**Star Schema Components**:

**Fact Table** (`fct_messages`):
- **Central table** with one row per message
- **Metrics**: `view_count`, `forward_count`, `message_length`
- **Keys**: Links to dimensions via `channel_key`, `message_date`
- **Supports**: Aggregation queries, metric analysis, trend calculation

**Dimension Tables**:

1. **`dim_channels`**:
   - **Fields**: `channel_name`, `total_posts`, `avg_views`, `avg_forwards`
   - **Analytical Need**: Competitive benchmarking
   - **Sample Query**: "Which channel has highest engagement rate?"

2. **`dim_dates`**:
   - **Fields**: `year`, `month`, `day`, `day_of_week`, `quarter`, `is_weekend`
   - **Analytical Need**: Time-series analysis, seasonality detection
   - **Sample Query**: "What's the posting frequency by day of week?"

**Why Star Schema?**:
- **Optimized for analytics**: Fast aggregations, simple joins
- **Business-friendly**: Non-technical users can understand table relationships
- **Scalable**: Easy to add new dimensions (e.g., `dim_products` in future)
- **Kimball methodology**: Proven approach for data warehousing

**Visual Aid**: Star schema diagram embedded (Figure 1) showing table relationships.

---

## ✅ Reflections on Data Quality and Next Steps

### Question 9: What data quality challenges emerged and how were they addressed?

**Answered in**: 
- **Section 2.1.3** (Pages 4-5): Error handling strategies
- **Section 2.2.3** (Pages 6-7): Missing data handling
- **Section 4.3** (Page 9): "Key Observations from Initial Data"

**Challenges Identified**:

**1. Telegram Rate Limiting**:
- **Challenge**: Bulk scraping triggers `FloodWaitError`
- **Solution**: Automatic sleep/retry logic with exponential backoff
- **Code shown**: `await asyncio.sleep(e.seconds)`

**2. Inconsistent Metadata**:
- **Challenge**: Some channels disable `views`/`forwards` counts → NULL values
- **Solution**: Staging layer converts NULL → 0 for metrics
- **Note in Report**: "Data Quality Note: Some fields occasionally NULL because channels disable forwarding"

**3. Image-Only Messages**:
- **Challenge**: Messages without text have NULL `message_text`
- **Solution**: Staging converts NULL text → empty string
- **Derived metric**: `has_media_flag` to identify visual-only content

**4. Duplicate Risk**:
- **Challenge**: Re-running scraper or loader could duplicate records
- **Solution**: 
  - Scraper: Checkpoint-based `min_id` prevents re-scraping
  - Loader: `SELECT 1 WHERE message_id = %s AND channel_name = %s` deduplication check

**5. Type Inconsistencies**:
- **Challenge**: JSON doesn't enforce types (views could be string)
- **Solution**: Staging layer explicit type casting + PostgreSQL schema enforcement

---

### Question 10: What are the remaining steps and anticipated challenges?

**Answered in**: **Section 3** (Pages 8-9): "Next Steps and Key Areas of Focus"

**Remaining Steps**:

**Task 3: YOLO Enrichment**:
- **Approach**: YOLOv8n model, detect `person`, `bottle`, `box`
- **Classification**: Promotional, Product Display, Lifestyle, Other
- **Integration**: `fct_image_detections` table joinable with `fct_messages`
- **Business Value**: "What imagery drives engagement?"

**Task 4: FastAPI Development**:
- **4 Endpoints planned**:
  1. `/api/reports/top-products` - Trending products
  2. `/api/channels/{name}/activity` - Time-series analysis
  3. `/api/search/messages` - Full-text search
  4. `/api/reports/visual-content` - Image classification stats
- **Validation**: Automated testing, Swagger UI, <200ms performance target

**Task 5: Dagster Orchestration**:
- **Scheduling**: Daily CRON at 2 AM ET
- **Dependency Management**: Software-Defined Assets approach
- **Monitoring**: Dagster UI for observability
- **Failure Handling**: Retry logic + Slack/email alerting

**Anticipated Challenges** (Section 3.2):

**Challenge 1: YOLO Deployment Environment**:
- **Issue**: Python 3.14/PyTorch incompatibility
- **Mitigation**: Separate Docker container (Python 3.10) OR cloud inference service OR mock for testing

**Challenge 2: API Performance at Scale**:
- **Issue**: Full-table scans at 10,000+ messages
- **Mitigation**: Database indexing, PostgreSQL full-text search (tsvector), Redis caching, pagination

**Challenge 3: Data Freshness vs. Rate Limits**:
- **Issue**: Hourly scraping may trigger rate limits
- **Mitigation**: Intelligent polling (activity-based), exponential backoff, channel prioritization

---

## Summary: Question Coverage

| Question Category | Questions | All Answered? | Primary Report Section |
|:------------------|:---------:|:-------------:|:-----------------------|
| **Business Alignment** | 2 | ✅ Yes | Sections 1.1, 1.3 |
| **Data Scraping (Task 1)** | 3 | ✅ Yes | Sections 2.1.1, 2.1.2, 2.1.3 |
| **Data Loading & Transformation (Task 2)** | 3 | ✅ Yes | Sections 2.2.2, 2.2.3, 2.2.4, 2.2.5 |
| **Data Quality Reflections** | 2 | ✅ Yes | Sections 2.1.3, 2.2.3, 3.2 |
| **TOTAL** | **10** | **✅ 10/10** | **Comprehensive Coverage** |

---

## Recommendation

**Your current Task 1-2 report already addresses all 10 required questions comprehensively.** The answers are well-structured and distributed logically throughout the report rather than in a rigid Q&A format, which makes for better narrative flow.

**Optional Enhancement**: If your instructor prefers explicit question-answer format, I can add an **"Appendix E: Questions Addressed"** section that directly lists each question with a concise answer + cross-reference to the full explanation in the main report.

Would you like me to add this appendix for extra clarity?
