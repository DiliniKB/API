from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, ListCreate, ListResponse
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Task endpoints
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task"""
    try:
        task = TaskService.create_task(db, current_user.id, task_data)
        return task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("", response_model=List[TaskResponse])
def get_tasks(
    list_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks for current user, optionally filtered by list"""
    tasks = TaskService.get_user_tasks(db, current_user.id, list_id)
    return tasks

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task"""
    try:
        task = TaskService.update_task(db, task_id, current_user.id, task_data)
        return task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task"""
    success = TaskService.delete_task(db, task_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return None

@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark task as complete"""
    try:
        task = TaskService.update_task(
            db, task_id, current_user.id, 
            TaskUpdate(completed=True)
        )
        return task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# List endpoints
@router.post("/lists", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
def create_list(
    list_data: ListCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new list"""
    list_obj = TaskService.create_list(db, current_user.id, list_data)
    return list_obj

@router.get("/lists", response_model=List[ListResponse])
def get_lists(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all lists for current user (creates defaults if none exist)"""
    lists = TaskService.get_or_create_default_lists(db, current_user.id)
    return lists