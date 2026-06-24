from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field

# Project schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the project folder")
    description: Optional[str] = Field(None, max_length=250, description="Short summary of the project focus")

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=250)

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    conversations_count: int = 0

    class Config:
        from_attributes = True

class PaginatedProjectResponse(BaseModel):
    total_items: int
    page: int
    size: int
    total_pages: int
    items: List[ProjectResponse]


# Conversation schemas
class ConversationBase(BaseModel):
    title: str = Field("New Conversation", max_length=150)
    chat_mode: str = Field("normal", description="normal or web_search")
    project_id: Optional[int] = Field(None, description="Linked project folder ID")
    assistant_id: int = Field(..., description="Linked assistant ID")

class ConversationCreate(BaseModel):
    project_id: Optional[int] = None
    assistant_id: int
    title: Optional[str] = "New Conversation"
    chat_mode: Optional[str] = "normal"

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    project_id: Optional[int] = None
    chat_mode: Optional[str] = None

class ConversationResponse(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    assistant_name: Optional[str] = None
    assistant_avatar: Optional[str] = None

    class Config:
        from_attributes = True

class PaginatedConversationResponse(BaseModel):
    total_items: int
    page: int
    size: int
    total_pages: int
    items: List[ConversationResponse]


# Message schemas
class MessageBase(BaseModel):
    role: str = Field(..., description="user, assistant, or system")
    content: str = Field(..., min_length=1, description="Message text content")

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, description="The user query text")

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: Optional[str] = None  # JSON string of web search sources
    created_at: datetime

    class Config:
        from_attributes = True


# Artifact schemas
class ArtifactBase(BaseModel):
    type: str = Field(..., description="code, markdown, json, sql, text")
    content: str = Field(..., description="Main workspace document content")

class ArtifactCreate(ArtifactBase):
    conversation_id: int

class ArtifactResponse(ArtifactBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Advanced Response payloads
class ChatResponsePayload(BaseModel):
    response: str = Field(..., description="The assistant's text response/summary")
    message_id: int = Field(..., description="Database ID of the assistant's message")
    conversation_id: int = Field(..., description="Parent thread ID")
    chat_mode: str = Field(..., description="Active conversation chat mode")
    sources: Optional[List[dict]] = Field(None, description="Extracted web search hits or references")
    retrieved_context_count: int = Field(0, description="RAG hit count")
    artifact: Optional[ArtifactResponse] = Field(None, description="Newly generated canvas document (if any)")
    warning: Optional[str] = None
