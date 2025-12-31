from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.schemas.entity import (
    EntityCreate, EntityUpdate, EntityResponse,
    EntityRelationCreate, EntityRelationResponse,
    ContextWindowCreate, ContextWindowResponse
)
from app.services.entity_service import EntityService

router = APIRouter(prefix="/entities", tags=["entities"])

# Entity endpoints
@router.post("", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(
    entity_data: EntityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new entity"""
    entity = EntityService.create_entity(db, current_user.id, entity_data)
    return entity

@router.get("", response_model=List[EntityResponse])
def get_entities(
    entity_type: Optional[str] = Query(None),
    context_tag: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all entities for current user with optional filters"""
    entities = EntityService.get_user_entities(db, current_user.id, entity_type, context_tag, status)
    return entities

@router.get("/{entity_id}", response_model=EntityResponse)
def get_entity(
    entity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific entity"""
    entity = EntityService.get_entity_by_id(db, entity_id, current_user.id)
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return entity

@router.put("/{entity_id}", response_model=EntityResponse)
def update_entity(
    entity_id: UUID,
    entity_data: EntityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an entity"""
    try:
        entity = EntityService.update_entity(db, entity_id, current_user.id, entity_data)
        return entity
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entity(
    entity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an entity"""
    success = EntityService.delete_entity(db, entity_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
    return None

# Relation endpoints
@router.post("/relations", response_model=EntityRelationResponse, status_code=status.HTTP_201_CREATED)
def create_relation(
    relation_data: EntityRelationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a relationship between entities"""
    relation = EntityService.create_relation(
        db, 
        relation_data.parent_id, 
        relation_data.child_id, 
        relation_data.relation_type
    )
    return relation

@router.get("/{entity_id}/relations", response_model=List[EntityRelationResponse])
def get_entity_relations(
    entity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all relationships for an entity"""
    relations = EntityService.get_entity_relations(db, entity_id)
    return relations

# Context window endpoints
@router.post("/context-windows", response_model=ContextWindowResponse, status_code=status.HTTP_201_CREATED)
def create_context_window(
    window_data: ContextWindowCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a context window"""
    window = EntityService.create_context_window(db, current_user.id, window_data)
    return window

@router.get("/context-windows", response_model=List[ContextWindowResponse])
def get_context_windows(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all context windows"""
    windows = EntityService.get_user_context_windows(db, current_user.id)
    return windows