from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    crop: Optional[str] = None
    language: Optional[str] = "en"
    context: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    success: bool = True
    answer: str
    language: str = "en"
    context_used: Optional[Dict[str, Any]] = None

class ChatHistoryItem(BaseModel):
    id: int
    question: str
    answer: str
    language: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    success: bool = True
    history: List[ChatHistoryItem]
