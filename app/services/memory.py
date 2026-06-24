import re
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app import models, schemas

class MemoryService:
    @staticmethod
    def get_memory(db: Session, memory_id: int) -> Optional[models.Memory]:
        return db.query(models.Memory).filter(models.Memory.id == memory_id).first()

    @staticmethod
    def get_memories(
        db: Session,
        user_id: str = "default_user",
        category: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[List[models.Memory], int]:
        """List user memories with filtering, searching, and pagination."""
        query = db.query(models.Memory).filter(models.Memory.user_id == user_id)

        if category:
            query = query.filter(models.Memory.category == category)
        
        if search:
            query = query.filter(models.Memory.memory_text.ilike(f"%{search}%"))

        total_count = query.count()
        items = query.order_by(models.Memory.created_at.desc()).offset(skip).limit(limit).all()
        return items, total_count

    @staticmethod
    def create_memory(db: Session, memory: schemas.MemoryCreate) -> models.Memory:
        db_memory = models.Memory(**memory.model_dump())
        db.add(db_memory)
        db.commit()
        db.refresh(db_memory)
        return db_memory

    @staticmethod
    def update_memory(db: Session, db_memory: models.Memory, memory_update: schemas.MemoryUpdate) -> models.Memory:
        update_data = memory_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_memory, key, value)
        db.commit()
        db.refresh(db_memory)
        return db_memory

    @staticmethod
    def delete_memory(db: Session, db_memory: models.Memory) -> None:
        db.delete(db_memory)
        db.commit()

    @staticmethod
    def extract_and_save_memories(db: Session, user_message: str, user_id: str = "default_user") -> List[models.Memory]:
        """
        Auto-extract memory fragments from user messages using regex heuristics.
        Supports personal details, professional background, and developer preferences.
        """
        new_memories = []
        text = user_message.strip()

        # Regular expressions for heuristics
        patterns = [
            # Professional: "I am a [professional role]"
            (r"\bi\s+am\s+a\s+([a-zA-Z0-9\s\-]+(?:\bdeveloper\b|\barchitect\b|\bdesigner\b|\bmanager\b|\bstudent\b|\bengineer\b))", "professional"),
            # Professional: "I work as [role]"
            (r"\bi\s+work\s+as\s+([a-zA-Z0-9\s\-]+)", "professional"),
            # Preferences: "I prefer [preference]"
            (r"\bi\s+prefer\s+([a-zA-Z0-9\s\-]+)", "preferences"),
            # Preferences: "I use [stack/tool]"
            (r"\bi\s+use\s+([a-zA-Z0-9\s\-+,#]+(?:\bframework\b|\bdatabase\b|\blibrary\b|\blanguage\b|\bpostgres\b|\bsqlite\b|\bpython\b|\bfastapi\b))", "preferences"),
            # Personal: "My name is [name]"
            (r"\bmy\s+name\s+is\s+([a-zA-Z\s]+)", "personal")
        ]

        for regex, category in patterns:
            match = re.search(regex, text, re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                # Clean punctuation if matched at end of sentence
                extracted = re.sub(r"[.!?]$", "", extracted)
                
                # Check for duplicates to prevent spamming database
                exists = db.query(models.Memory).filter(
                    models.Memory.user_id == user_id,
                    models.Memory.category == category,
                    models.Memory.memory_text.ilike(f"%{extracted}%")
                ).first()

                if not exists:
                    # Save memory text
                    mem_text = f"User stated: '{match.group(0).strip()}' (Parsed: {extracted})"
                    db_mem = models.Memory(
                        user_id=user_id,
                        memory_text=mem_text,
                        category=category
                    )
                    db.add(db_mem)
                    new_memories.append(db_mem)
        
        if new_memories:
            db.commit()
            for m in new_memories:
                db.refresh(m)

        return new_memories

memory_service = MemoryService()
