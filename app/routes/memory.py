import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from app import schemas, models, database
from app.services.memory import memory_service
from app.utils.security import verify_api_key

router = APIRouter(
    prefix="/memories",
    tags=["Memory"],
    dependencies=[Depends(verify_api_key)]
)

@router.post("/", response_model=schemas.MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(memory: schemas.MemoryCreate, db: Session = Depends(database.get_db)):
    """Create a new manual user memory."""
    return memory_service.create_memory(db=db, memory=memory)


@router.get("/", response_model=schemas.PaginatedMemoryResponse)
def list_memories(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    user_id: str = Query("default_user"),
    db: Session = Depends(database.get_db)
):
    """List user memories with pagination, category filter, and keyword search."""
    skip = (page - 1) * size
    items, total_items = memory_service.get_memories(
        db=db,
        user_id=user_id,
        category=category,
        search=search,
        skip=skip,
        limit=size
    )
    total_pages = math.ceil(total_items / size) if total_items > 0 else 0
    
    return schemas.PaginatedMemoryResponse(
        total_items=total_items,
        page=page,
        size=size,
        total_pages=total_pages,
        items=items
    )


@router.put("/{memory_id}", response_model=schemas.MemoryResponse)
def update_memory(
    memory_id: int,
    memory_update: schemas.MemoryUpdate,
    db: Session = Depends(database.get_db)
):
    """Update a specific memory entry."""
    db_memory = memory_service.get_memory(db=db, memory_id=memory_id)
    if not db_memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory with ID {memory_id} not found"
        )
    return memory_service.update_memory(db=db, db_memory=db_memory, memory_update=memory_update)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(memory_id: int, db: Session = Depends(database.get_db)):
    """Delete a memory entry by ID."""
    db_memory = memory_service.get_memory(db=db, memory_id=memory_id)
    if not db_memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory with ID {memory_id} not found"
        )
    memory_service.delete_memory(db=db, db_memory=db_memory)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
