from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatQueryRequest(BaseModel):
    question: str
    page_context: Optional[str] = "dashboard"

class ChatQueryResponse(BaseModel):
    id: int
    question: str
    answer: str
    page_context: Optional[str]
    timestamp: datetime
