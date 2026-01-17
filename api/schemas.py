from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# --- Base Models ---

class MessageBase(BaseModel):
    message_id: int
    channel_name: str
    message_date: datetime
    message_text: Optional[str] = None
    views: int
    forwards: int

    class Config:
        from_attributes = True

# --- Report Models ---

class TopProductResponse(BaseModel):
    product_name: str
    mention_count: int

class ChannelActivityResponse(BaseModel):
    date: str
    message_count: int
    total_views: int

class VisualContentResponse(BaseModel):
    image_category: str
    count: int
    avg_confidence: float

class SearchResponse(BaseModel):
    total_results: int
    results: List[MessageBase]
