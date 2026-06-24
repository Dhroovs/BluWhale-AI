from sqlalchemy.orm import Session
from app import models, schemas

def get_knowledge_base(db: Session, kb_id: int) -> models.KnowledgeBase:
    """Retrieve a single knowledge base document by its ID."""
    return db.query(models.KnowledgeBase).filter(models.KnowledgeBase.id == kb_id).first()


def get_knowledge_bases(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str = None,
    data_source: str = None,
    chatbot_id: int = None,
    assistant_id: int = None
):
    """
    Retrieve knowledge bases with searching (by name/content),
    filtering (by data source, owner chatbot ID, or assistant ID), and pagination.
    Returns a tuple of (items, total_count).
    """
    query = db.query(models.KnowledgeBase)

    # Search filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.KnowledgeBase.name.ilike(search_filter)) |
            (models.KnowledgeBase.content.ilike(search_filter))
        )

    # Data source filter (text, file, url, database)
    if data_source:
        query = query.filter(models.KnowledgeBase.data_source == data_source)

    # Chatbot owner filter
    if chatbot_id is not None:
        query = query.filter(models.KnowledgeBase.chatbot_id == chatbot_id)

    # Assistant owner filter
    if assistant_id is not None:
        query = query.filter(models.KnowledgeBase.assistant_id == assistant_id)

    total_count = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return items, total_count


from app.utils.text_splitter import split_text

def create_knowledge_base(db: Session, kb: schemas.KnowledgeBaseCreate) -> models.KnowledgeBase:
    """Create a new knowledge base item and attach it to a chatbot. Auto-chunks text."""
    db_kb = models.KnowledgeBase(**kb.model_dump())
    db.add(db_kb)
    db.commit()
    db.refresh(db_kb)

    # Generate and persist chunks
    chunks = split_text(db_kb.content)
    for idx, chunk_content in enumerate(chunks):
        db_chunk = models.KnowledgeBaseChunk(
            knowledge_base_id=db_kb.id,
            chunk_index=idx,
            content=chunk_content
        )
        db.add(db_chunk)
    db.commit()
    db.refresh(db_kb)
    return db_kb


def update_knowledge_base(
    db: Session,
    db_kb: models.KnowledgeBase,
    kb_update: schemas.KnowledgeBaseUpdate
) -> models.KnowledgeBase:
    """Perform a partial update on a knowledge base document. Re-chunks if content changes."""
    update_data = kb_update.model_dump(exclude_unset=True)
    content_changed = "content" in update_data and update_data["content"] != db_kb.content

    for key, value in update_data.items():
        setattr(db_kb, key, value)
        
    db.commit()

    if content_changed:
        # Delete old chunks
        db.query(models.KnowledgeBaseChunk).filter(models.KnowledgeBaseChunk.knowledge_base_id == db_kb.id).delete()
        db.commit()

        # Generate and save new chunks
        chunks = split_text(db_kb.content)
        for idx, chunk_content in enumerate(chunks):
            db_chunk = models.KnowledgeBaseChunk(
                knowledge_base_id=db_kb.id,
                chunk_index=idx,
                content=chunk_content
            )
            db.add(db_chunk)
        db.commit()

    db.refresh(db_kb)
    return db_kb



def delete_knowledge_base(db: Session, db_kb: models.KnowledgeBase) -> None:
    """Delete a knowledge base document."""
    db.delete(db_kb)
    db.commit()
