from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Assistant(Base):
    __tablename__ = "assistants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(250), nullable=True)
    system_prompt = Column(Text, default="You are a helpful AI assistant.", nullable=True)
    avatar = Column(String(100), default="fa-solid fa-robot", nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Conversations using this assistant
    conversations = relationship("Conversation", back_populates="assistant", cascade="all, delete-orphan")
    
    # Knowledge Base linked to this assistant for RAG query context
    knowledge_bases = relationship("KnowledgeBase", back_populates="assistant", cascade="all, delete-orphan")
