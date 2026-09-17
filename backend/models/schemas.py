from datetime import date
from typing import List
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation: List[ChatMessage] = []


class AvailabilityRequest(BaseModel):
    check_in: date
    check_out: date
    adults: int = Field(ge=1)
