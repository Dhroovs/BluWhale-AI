import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import services, schemas, database, models

from fastapi import File, Form, UploadFile
from app.utils.security import verify_api_key
from pydantic import BaseModel, Field

class URLScrapeRequest(BaseModel):
    url: str = Field(..., description="The HTTP/HTTPS URL to scrape")
    chatbot_id: Optional[int] = Field(None, description="The target chatbot ID to link")
    assistant_id: Optional[int] = Field(None, description="The target assistant ID to link")
    name: str = Field(..., min_length=1, max_length=100, description="The name of the knowledge source")
    description: Optional[str] = Field(None, max_length=250, description="Brief description")

router = APIRouter(
    prefix="/knowledge-bases",
    tags=["Knowledge Bases"],
    dependencies=[Depends(verify_api_key)]
)


@router.post("/", response_model=schemas.KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
def create_new_knowledge_base(
    kb: schemas.KnowledgeBaseCreate,
    db: Session = Depends(database.get_db)
):
    """
    Create a new Knowledge Base document and link it to an Assistant or Chatbot agent.
    """
    if kb.assistant_id:
        assistant = db.query(models.Assistant).filter(models.Assistant.id == kb.assistant_id).first()
        if not assistant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create Knowledge Base: Assistant with ID {kb.assistant_id} does not exist"
            )
    elif kb.chatbot_id:
        chatbot = services.get_chatbot(db=db, chatbot_id=kb.chatbot_id)
        if not chatbot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot create Knowledge Base: Chatbot with ID {kb.chatbot_id} does not exist"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create Knowledge Base: Must specify either chatbot_id or assistant_id"
        )
        
    # Auto-scrape if data_source is url and content is an HTTP link
    if kb.data_source == "url" and (kb.content.startswith("http://") or kb.content.startswith("https://")):
        from app.utils.extractor import extract_text_from_url
        kb.content = extract_text_from_url(kb.content)
        
    return services.create_knowledge_base(db=db, kb=kb)


@router.get("/", response_model=schemas.PaginatedKnowledgeBaseResponse)
def list_knowledge_bases(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    size: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    search: Optional[str] = Query(None, description="Search term for name/content"),
    data_source: Optional[str] = Query(None, description="Filter by data source type"),
    chatbot_id: Optional[int] = Query(None, description="Filter by owner chatbot ID"),
    assistant_id: Optional[int] = Query(None, description="Filter by owner assistant ID"),
    db: Session = Depends(database.get_db)
):
    """
    List Knowledge Base documents with filtering, searching, and pagination.
    """
    skip = (page - 1) * size
    
    items, total_items = services.get_knowledge_bases(
        db=db,
        skip=skip,
        limit=size,
        search=search,
        data_source=data_source,
        chatbot_id=chatbot_id,
        assistant_id=assistant_id
    )
    
    total_pages = math.ceil(total_items / size) if total_items > 0 else 0
    
    return schemas.PaginatedKnowledgeBaseResponse(
        total_items=total_items,
        page=page,
        size=size,
        total_pages=total_pages,
        items=items
    )


@router.get("/{kb_id}", response_model=schemas.KnowledgeBaseResponse)
def get_knowledge_base_details(kb_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieve details for a single knowledge base by ID.
    """
    db_kb = services.get_knowledge_base(db=db, kb_id=kb_id)
    if not db_kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge Base with ID {kb_id} not found"
        )
    return db_kb


@router.put("/{kb_id}", response_model=schemas.KnowledgeBaseResponse)
def update_knowledge_base_details(
    kb_id: int,
    kb_update: schemas.KnowledgeBaseUpdate,
    db: Session = Depends(database.get_db)
):
    """
    Update an existing knowledge base (partial updates allowed).
    
    If updating the chatbot link, verifies that the new chatbot ID exists first.
    """
    db_kb = services.get_knowledge_base(db=db, kb_id=kb_id)
    if not db_kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge Base with ID {kb_id} not found"
        )
        
    # If the user is trying to change which chatbot this knowledge base is attached to,
    # verify that the new chatbot exists first.
    if kb_update.chatbot_id is not None:
        new_chatbot = services.get_chatbot(db=db, chatbot_id=kb_update.chatbot_id)
        if not new_chatbot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update Knowledge Base: Chatbot with ID {kb_update.chatbot_id} does not exist"
            )
            
    return services.update_knowledge_base(db=db, db_kb=db_kb, kb_update=kb_update)


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_base_record(kb_id: int, db: Session = Depends(database.get_db)):
    """
    Delete a knowledge base record by ID.
    
    Returns HTTP 204 No Content upon success.
    """
    db_kb = services.get_knowledge_base(db=db, kb_id=kb_id)
    if not db_kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge Base with ID {kb_id} not found"
        )
    services.delete_knowledge_base(db=db, db_kb=db_kb)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/upload", response_model=schemas.KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def upload_knowledge_base_file(
    file: UploadFile = File(...),
    chatbot_id: Optional[int] = Form(None),
    assistant_id: Optional[int] = Form(None),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(database.get_db)
):
    """
    Upload a document (PDF or TXT/MD), extract its text, and store/chunk it.
    """
    if assistant_id:
        assistant = db.query(models.Assistant).filter(models.Assistant.id == assistant_id).first()
        if not assistant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot upload Knowledge Base: Assistant with ID {assistant_id} does not exist"
            )
    elif chatbot_id:
        chatbot = services.get_chatbot(db=db, chatbot_id=chatbot_id)
        if not chatbot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot upload Knowledge Base: Chatbot with ID {chatbot_id} does not exist"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload Knowledge Base: Must specify either chatbot_id or assistant_id"
        )
        
    file_bytes = await file.read()
    from app.utils.extractor import extract_text_from_file
    extracted_content = extract_text_from_file(file_bytes, file.filename)
    
    kb_create = schemas.KnowledgeBaseCreate(
        name=name,
        description=description,
        data_source="file",
        content=extracted_content,
        chatbot_id=chatbot_id,
        assistant_id=assistant_id
    )
    return services.create_knowledge_base(db=db, kb=kb_create)


@router.post("/scrape", response_model=schemas.KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
def scrape_knowledge_base_url(
    payload: URLScrapeRequest,
    db: Session = Depends(database.get_db)
):
    """
    Scrape text content from a web page URL, clean it up, and store/chunk it.
    """
    if payload.assistant_id:
        assistant = db.query(models.Assistant).filter(models.Assistant.id == payload.assistant_id).first()
        if not assistant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot scrape Knowledge Base: Assistant with ID {payload.assistant_id} does not exist"
            )
    elif payload.chatbot_id:
        chatbot = services.get_chatbot(db=db, chatbot_id=payload.chatbot_id)
        if not chatbot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot scrape Knowledge Base: Chatbot with ID {payload.chatbot_id} does not exist"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot scrape Knowledge Base: Must specify either chatbot_id or assistant_id"
        )
        
    from app.utils.extractor import extract_text_from_url
    extracted_content = extract_text_from_url(payload.url)
    
    kb_create = schemas.KnowledgeBaseCreate(
        name=payload.name,
        description=payload.description,
        data_source="url",
        content=extracted_content,
        chatbot_id=payload.chatbot_id,
        assistant_id=payload.assistant_id
    )
    return services.create_knowledge_base(db=db, kb=kb_create)
