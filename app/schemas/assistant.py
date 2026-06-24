from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class AssistantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the custom assistant")
    description: Optional[str] = Field(None, max_length=250, description="Short purpose statement")
    system_prompt: Optional[str] = Field("You are a helpful AI assistant.", description="Instructions guiding the agent's behavior")
    avatar: Optional[str] = Field("fa-solid fa-robot", max_length=100, description="Icon styling class name")

class AssistantCreate(AssistantBase):
    pass

class AssistantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=250)
    system_prompt: Optional[str] = Field(None)
    avatar: Optional[str] = Field(None, max_length=100)

class AssistantResponse(AssistantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedAssistantResponse(BaseModel):
    total_items: int
    page: int
    size: int
    total_pages: int
    items: List[AssistantResponse]
