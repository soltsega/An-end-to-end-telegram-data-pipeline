from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageBase(BaseModel):
    message_id: int
    channel_name: str
    message_date: datetime
    message_text: Optional[str] = None
    has_media: bool
    image_path: Optional[str] = None
    views: int
    forwards: int

class Message(MessageBase):
    class Config:
        orm_mode = True
