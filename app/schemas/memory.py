from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class MemoryBase(BaseModel):
    memory_text: str = Field(..., min_length=1, description="The specific user statement/preference to remember")
    category: str = Field("custom", description="Category of memory: personal, professional, preferences, custom")

class MemoryCreate(MemoryBase):
    user_id: Optional[str] = Field("default_user", description="Identifier of the scoped user")

class MemoryUpdate(BaseModel):
    memory_text: Optional[str] = Field(None)
    category: Optional[str] = Field(None)

class MemoryResponse(MemoryBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedMemoryResponse(BaseModel):
    total_items: int
    page: int
    size: int
    total_pages: int
    items: List[MemoryResponse]
