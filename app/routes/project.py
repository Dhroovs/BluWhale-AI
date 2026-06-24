import math
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status, Header
from sqlalchemy.orm import Session
from app import schemas, models, database
from app.services.chat import chat_service
from app.utils.security import verify_api_key

router = APIRouter(
    tags=["Projects & Conversations"],
    dependencies=[Depends(verify_api_key)]
)


# ----------------- PROJECTS ENDPOINTS -----------------

@router.post("/projects", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db)):
    """Create a new project workspace folder."""
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/projects", response_model=schemas.PaginatedProjectResponse)
def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(database.get_db)
):
    """List project folders with pagination and name filters."""
    query = db.query(models.Project)
    if search:
        query = query.filter(models.Project.name.ilike(f"%{search}%"))
        
    total_items = query.count()
    skip = (page - 1) * size
    items = query.order_by(models.Project.created_at.desc()).offset(skip).limit(size).all()
    
    # Calculate conversation counts manually for the response schemas
    response_items = []
    for item in items:
        count = db.query(models.Conversation).filter(models.Conversation.project_id == item.id).count()
        res = schemas.ProjectResponse.model_validate(item)
        res.conversations_count = count
        response_items.append(res)
        
    total_pages = math.ceil(total_items / size) if total_items > 0 else 0
    return schemas.PaginatedProjectResponse(
        total_items=total_items,
        page=page,
        size=size,
        total_pages=total_pages,
        items=response_items
    )


@router.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(database.get_db)):
    """Retrieve details for a single project folder."""
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
    count = db.query(models.Conversation).filter(models.Conversation.project_id == project_id).count()
    res = schemas.ProjectResponse.model_validate(db_project)
    res.conversations_count = count
    return res


@router.put("/projects/{project_id}", response_model=schemas.ProjectResponse)
def update_project(project_id: int, project_update: schemas.ProjectUpdate, db: Session = Depends(database.get_db)):
    """Rename or modify a project workspace."""
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
        
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
        
    db.commit()
    db.refresh(db_project)
    
    count = db.query(models.Conversation).filter(models.Conversation.project_id == project_id).count()
    res = schemas.ProjectResponse.model_validate(db_project)
    res.conversations_count = count
    return res


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(database.get_db)):
    """Delete a project. Cascades deletions to conversation threads and messages."""
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
    db.delete(db_project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ----------------- CONVERSATIONS ENDPOINTS -----------------

@router.post("/conversations", response_model=schemas.ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(conv: schemas.ConversationCreate, db: Session = Depends(database.get_db)):
    """Start a new conversation thread linked to an assistant, optionally inside a project."""
    # Check that assistant exists
    assistant = db.query(models.Assistant).filter(models.Assistant.id == conv.assistant_id).first()
    if not assistant:
        raise HTTPException(status_code=404, detail=f"Assistant with ID {conv.assistant_id} not found")
        
    # Check that project exists if provided
    if conv.project_id:
        proj = db.query(models.Project).filter(models.Project.id == conv.project_id).first()
        if not proj:
            raise HTTPException(status_code=404, detail=f"Project with ID {conv.project_id} not found")

    db_conv = models.Conversation(**conv.model_dump())
    db.add(db_conv)
    db.commit()
    db.refresh(db_conv)
    
    res = schemas.ConversationResponse.model_validate(db_conv)
    res.assistant_name = assistant.name
    res.assistant_avatar = assistant.avatar
    return res


@router.get("/conversations", response_model=schemas.PaginatedConversationResponse)
def list_conversations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    project_id: Optional[int] = Query(None),
    assistant_id: Optional[int] = Query(None),
    db: Session = Depends(database.get_db)
):
    """List conversation threads with optional filtering by project or assistant."""
    query = db.query(models.Conversation)
    if project_id is not None:
        query = query.filter(models.Conversation.project_id == project_id)
    if assistant_id is not None:
        query = query.filter(models.Conversation.assistant_id == assistant_id)
        
    total_items = query.count()
    skip = (page - 1) * size
    items = query.order_by(models.Conversation.updated_at.desc()).offset(skip).limit(size).all()
    
    response_items = []
    for item in items:
        res = schemas.ConversationResponse.model_validate(item)
        if item.assistant:
            res.assistant_name = item.assistant.name
            res.assistant_avatar = item.assistant.avatar
        response_items.append(res)
        
    total_pages = math.ceil(total_items / size) if total_items > 0 else 0
    return schemas.PaginatedConversationResponse(
        total_items=total_items,
        page=page,
        size=size,
        total_pages=total_pages,
        items=response_items
    )


@router.get("/conversations/{conversation_id}", response_model=schemas.ConversationResponse)
def get_conversation(conversation_id: int, db: Session = Depends(database.get_db)):
    """Retrieve details for a single conversation thread."""
    db_conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not db_conv:
        raise HTTPException(status_code=404, detail=f"Conversation with ID {conversation_id} not found")
    res = schemas.ConversationResponse.model_validate(db_conv)
    if db_conv.assistant:
        res.assistant_name = db_conv.assistant.name
        res.assistant_avatar = db_conv.assistant.avatar
    return res


@router.put("/conversations/{conversation_id}", response_model=schemas.ConversationResponse)
def update_conversation(
    conversation_id: int,
    conv_update: schemas.ConversationUpdate,
    db: Session = Depends(database.get_db)
):
    """Update conversation properties (rename title, move to a project, or switch chat mode)."""
    db_conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not db_conv:
        raise HTTPException(status_code=404, detail=f"Conversation with ID {conversation_id} not found")
        
    update_data = conv_update.model_dump(exclude_unset=True)
    
    # Validate project_id if it is changing
    if "project_id" in update_data and update_data["project_id"] is not None:
        proj = db.query(models.Project).filter(models.Project.id == update_data["project_id"]).first()
        if not proj:
            raise HTTPException(status_code=404, detail=f"Project with ID {update_data['project_id']} not found")

    for key, value in update_data.items():
        setattr(db_conv, key, value)
        
    db.commit()
    db.refresh(db_conv)
    
    res = schemas.ConversationResponse.model_validate(db_conv)
    if db_conv.assistant:
        res.assistant_name = db_conv.assistant.name
        res.assistant_avatar = db_conv.assistant.avatar
    return res


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: int, db: Session = Depends(database.get_db)):
    """Delete a conversation thread and its associated message logs."""
    db_conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not db_conv:
        raise HTTPException(status_code=404, detail=f"Conversation with ID {conversation_id} not found")
    db.delete(db_conv)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ----------------- MESSAGES & CHAT ENDPOINTS -----------------

@router.get("/conversations/{conversation_id}/messages", response_model=List[schemas.MessageResponse])
def get_conversation_messages(conversation_id: int, db: Session = Depends(database.get_db)):
    """Retrieve all message logs in chronological order for a single thread."""
    db_conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not db_conv:
        raise HTTPException(status_code=404, detail=f"Conversation with ID {conversation_id} not found")
    return db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id
    ).order_by(models.Message.created_at.asc()).all()


@router.post("/conversations/{conversation_id}/messages", response_model=schemas.ChatResponsePayload)
def send_chat_message(
    conversation_id: int,
    payload: schemas.MessageCreate,
    x_grok_api_key: Optional[str] = Header(None, alias="X-Grok-API-Key"),
    db: Session = Depends(database.get_db)
):
    """
    Append a user message to a thread and process the assistant's response.
    Triggers RAG retrieval, memories injection, search providers (if search mode enabled), 
    and checks for code outputs to save as Artifact Canvas documents.
    """
    result = chat_service.process_chat_message(
        db=db,
        conversation_id=conversation_id,
        user_message_text=payload.content,
        user_id="default_user",
        override_grok_key=x_grok_api_key
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"Conversation or Assistant not found")
    return result


# ----------------- ARTIFACTS ENDPOINTS -----------------

@router.get("/conversations/{conversation_id}/artifacts", response_model=List[schemas.ArtifactResponse])
def list_conversation_artifacts(conversation_id: int, db: Session = Depends(database.get_db)):
    """Retrieve all Canvas Artifact documents created in a conversation thread."""
    db_conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not db_conv:
        raise HTTPException(status_code=404, detail=f"Conversation with ID {conversation_id} not found")
    return db.query(models.Artifact).filter(
        models.Artifact.conversation_id == conversation_id
    ).order_by(models.Artifact.created_at.desc()).all()


@router.get("/artifacts/{artifact_id}", response_model=schemas.ArtifactResponse)
def get_artifact(artifact_id: int, db: Session = Depends(database.get_db)):
    """Retrieve details for a single Canvas Artifact document by ID."""
    db_art = db.query(models.Artifact).filter(models.Artifact.id == artifact_id).first()
    if not db_art:
        raise HTTPException(status_code=404, detail=f"Artifact with ID {artifact_id} not found")
    return db_art
