from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.models import Task, List as ListModel, User
from app.schemas.task import TaskCreate, TaskUpdate, ListCreate

class TaskService:
    
    @staticmethod
    def create_task(db: Session, user_id: UUID, task_data: TaskCreate) -> Task:
        """Create a new task"""
        # Verify list belongs to user
        list_obj = db.query(ListModel).filter(
            ListModel.id == task_data.list_id,
            ListModel.user_id == user_id
        ).first()
        
        if not list_obj:
            raise ValueError("List not found or doesn't belong to user")
        
        task = Task(
            user_id=user_id,
            list_id=task_data.list_id,
            title=task_data.title,
            description=task_data.description,
            deadline=task_data.deadline,
            priority=task_data.priority
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def get_user_tasks(db: Session, user_id: UUID, list_id: Optional[UUID] = None) -> List[Task]:
        """Get all tasks for a user, optionally filtered by list"""
        query = db.query(Task).filter(Task.user_id == user_id)
        
        if list_id:
            query = query.filter(Task.list_id == list_id)
        
        return query.order_by(Task.priority.desc(), Task.created_at.desc()).all()
    
    @staticmethod
    def update_task(db: Session, task_id: UUID, user_id: UUID, task_data: TaskUpdate) -> Task:
        """Update a task"""
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()
        
        if not task:
            raise ValueError("Task not found")
        
        # Update fields
        update_data = task_data.model_dump(exclude_unset=True)
        
        # Handle completion timestamp
        if "completed" in update_data and update_data["completed"] and not task.completed:
            update_data["completed_at"] = datetime.utcnow()
        elif "completed" in update_data and not update_data["completed"]:
            update_data["completed_at"] = None
        
        for field, value in update_data.items():
            setattr(task, field, value)
        
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def delete_task(db: Session, task_id: UUID, user_id: UUID) -> bool:
        """Delete a task"""
        task = db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()
        
        if not task:
            return False
        
        db.delete(task)
        db.commit()
        return True
    
    @staticmethod
    def create_list(db: Session, user_id: UUID, list_data: ListCreate) -> ListModel:
        """Create a new list"""
        list_obj = ListModel(
            user_id=user_id,
            name=list_data.name,
            is_default=list_data.is_default
        )
        db.add(list_obj)
        db.commit()
        db.refresh(list_obj)
        return list_obj
    
    @staticmethod
    def get_user_lists(db: Session, user_id: UUID) -> List[ListModel]:
        """Get all lists for a user"""
        return db.query(ListModel).filter(ListModel.user_id == user_id).all()
    
    @staticmethod
    def get_or_create_default_lists(db: Session, user_id: UUID) -> List[ListModel]:
        """Create default lists (Town, Home, Free Time) if they don't exist"""
        default_names = ["Town", "Home", "Free Time"]
        existing_lists = db.query(ListModel).filter(
            ListModel.user_id == user_id,
            ListModel.is_default == True
        ).all()
        
        existing_names = {lst.name for lst in existing_lists}
        
        for name in default_names:
            if name not in existing_names:
                list_obj = ListModel(
                    user_id=user_id,
                    name=name,
                    is_default=True
                )
                db.add(list_obj)
        
        db.commit()
        return db.query(ListModel).filter(ListModel.user_id == user_id).all()