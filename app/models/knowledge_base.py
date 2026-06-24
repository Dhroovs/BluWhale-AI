from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(250), nullable=True)
    data_source = Column(String(50), default="text", nullable=False)  # text, file, url, database
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Link to a specific chatbot (optional now)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id", ondelete="CASCADE"), nullable=True)
    
    # Link to a custom assistant (optional)
    assistant_id = Column(Integer, ForeignKey("assistants.id", ondelete="CASCADE"), nullable=True)
    
    # Back relationships
    chatbot = relationship("Chatbot", back_populates="knowledge_bases")
    assistant = relationship("Assistant", back_populates="knowledge_bases")

    # Linked chunks
    chunks = relationship(
        "KnowledgeBaseChunk",
        back_populates="knowledge_base",
        cascade="all, delete-orphan"
    )


class KnowledgeBaseChunk(Base):
    __tablename__ = "knowledge_base_chunks"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    knowledge_base = relationship("KnowledgeBase", back_populates="chunks")

