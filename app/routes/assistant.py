import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from app import schemas, models, database
from app.utils.security import verify_api_key

router = APIRouter(
    prefix="/assistants",
    tags=["Assistants"],
    dependencies=[Depends(verify_api_key)]
)

@router.post("/", response_model=schemas.AssistantResponse, status_code=status.HTTP_201_CREATED)
def create_assistant(assistant: schemas.AssistantCreate, db: Session = Depends(database.get_db)):
    """Create a new custom assistant agent."""
    db_assistant = models.Assistant(**assistant.model_dump())
    db.add(db_assistant)
    db.commit()
    db.refresh(db_assistant)
    return db_assistant


@router.get("/", response_model=schemas.PaginatedAssistantResponse)
def list_assistants(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(database.get_db)
):
    """List custom assistants with search filtering and pagination."""
    query = db.query(models.Assistant)
    
    if search:
        query = query.filter(
            (models.Assistant.name.ilike(f"%{search}%")) |
            (models.Assistant.description.ilike(f"%{search}%"))
        )
        
    total_items = query.count()
    skip = (page - 1) * size
    items = query.order_by(models.Assistant.created_at.desc()).offset(skip).limit(size).all()
    total_pages = math.ceil(total_items / size) if total_items > 0 else 0
    
    return schemas.PaginatedAssistantResponse(
        total_items=total_items,
        page=page,
        size=size,
        total_pages=total_pages,
        items=items
    )


@router.get("/{assistant_id}", response_model=schemas.AssistantResponse)
def get_assistant(assistant_id: int, db: Session = Depends(database.get_db)):
    """Retrieve details for a single custom assistant agent by its unique ID."""
    db_assistant = db.query(models.Assistant).filter(models.Assistant.id == assistant_id).first()
    if not db_assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assistant with ID {assistant_id} not found"
        )
    return db_assistant


@router.put("/{assistant_id}", response_model=schemas.AssistantResponse)
def update_assistant(
    assistant_id: int,
    assistant_update: schemas.AssistantUpdate,
    db: Session = Depends(database.get_db)
):
    """Update details for an existing assistant agent."""
    db_assistant = db.query(models.Assistant).filter(models.Assistant.id == assistant_id).first()
    if not db_assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assistant with ID {assistant_id} not found"
        )
        
    update_data = assistant_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_assistant, key, value)
        
    db.commit()
    db.refresh(db_assistant)
    return db_assistant


@router.delete("/{assistant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assistant(assistant_id: int, db: Session = Depends(database.get_db)):
    """Delete an assistant agent. Cascades conversation deletions."""
    db_assistant = db.query(models.Assistant).filter(models.Assistant.id == assistant_id).first()
    if not db_assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assistant with ID {assistant_id} not found"
        )
        
    db.delete(db_assistant)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
