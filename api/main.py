from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from .database import get_db
from .schemas import (
    TopProductResponse, 
    ChannelActivityResponse, 
    VisualContentResponse, 
    SearchResponse,
    MessageBase
)

app = FastAPI(
    title="Medical Telegram Warehouse API",
    description="Analytical API for Ethiopian Medical Business Intelligence",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Medical Telegram Warehouse API. Visit /docs for documentation."}

# --- Endpoint 1: Top Products ---
@app.get("/api/reports/top-products", response_model=List[TopProductResponse])
def get_top_products(limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns the most frequently mentioned medical terms/products.
    Note: Ideally this uses a pre-calculated NLP table. 
    For now, we will perform a simple keyword frequency on the message text.
    """
    # This is a simplified example. In production, you'd use a dedicated 'products' dimension or NLP results.
    # Here we assume products are significant words in the text.
    query = text("""
        SELECT 
            substring(lower(message_text) from '\\w+') as product_name, 
            COUNT(*) as mention_count
        FROM public.fct_messages
        WHERE message_text IS NOT NULL
        GROUP BY product_name
        ORDER BY mention_count DESC
        LIMIT :limit
    """)
    results = db.execute(query, {"limit": limit}).fetchall()
    return [{"product_name": r[0], "mention_count": r[1]} for r in results]

# --- Endpoint 2: Channel Activity ---
@app.get("/api/channels/{channel_name}/activity", response_model=List[ChannelActivityResponse])
def get_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    """
    Returns daily posting activity and total views for a specific channel.
    """
    query = text("""
        SELECT 
            d.full_date::text as date,
            COUNT(m.message_id) as message_count,
            SUM(m.view_count) as total_views
        FROM public.fct_messages m
        JOIN public.dim_channels c ON m.channel_key = c.channel_key
        JOIN public.dim_dates d ON m.date_key = d.date_key
        WHERE c.channel_name = :channel_name
        GROUP BY d.full_date
        ORDER BY d.full_date ASC
    """)
    results = db.execute(query, {"channel_name": channel_name}).fetchall()
    
    if not results:
        raise HTTPException(status_code=404, detail="Channel not found or no data available")
        
    return [
        {"date": str(r[0]), "message_count": r[1], "total_views": r[2] or 0} 
        for r in results
    ]

# --- Endpoint 3: Message Search ---
@app.get("/api/search/messages", response_model=SearchResponse)
def search_messages(
    query: str, 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    """
    Searches for messages containing a specific keyword.
    """
    sql_query = text("""
        SELECT 
            m.message_id,
            c.channel_name,
            d.full_date + m.created_at::time as message_date,
            m.message_text,
            m.view_count as views,
            m.forward_count as forwards
        FROM public.fct_messages m
        JOIN public.dim_channels c ON m.channel_key = c.channel_key
        JOIN public.dim_dates d ON m.date_key = d.date_key
        WHERE m.message_text ILIKE :search_query
        ORDER BY d.full_date DESC
        LIMIT :limit
    """)
    results = db.execute(sql_query, {"search_query": f"%{query}%", "limit": limit}).fetchall()
    
    messages = [
        MessageBase(
            message_id=r[0],
            channel_name=r[1],
            message_date=r[2],
            message_text=r[3],
            views=r[4],
            forwards=r[5]
        ) for r in results
    ]
    
    return SearchResponse(total_results=len(messages), results=messages)

# --- Endpoint 4: Visual Content Stats ---
@app.get("/api/reports/visual-content", response_model=List[VisualContentResponse])
def get_visual_content_stats(db: Session = Depends(get_db)):
    """
    Returns statistics about image usage across channels based on YOLO detection.
    """
    # Check if table exists first (in case Task 3 hasn't run yet)
    try:
        query = text("""
            SELECT 
                image_category,
                COUNT(*) as count,
                AVG(confidence_scores::float) as avg_confidence -- Simplified casting, assuming single score for primary object
            FROM public.fct_image_detections
            GROUP BY image_category
            ORDER BY count DESC
        """)
        results = db.execute(query).fetchall()
        return [
            {"image_category": r[0], "count": r[1], "avg_confidence": r[2] or 0.0} 
            for r in results
        ]
    except Exception:
        # Fallback if table doesn't exist yet
        return []
