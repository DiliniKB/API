from langchain_core.tools import tool
from typing import Optional
from uuid import UUID
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, ListCreate

# Global context holder (will be set per request)
_context = {}

def set_agent_context(db, user_id: UUID):
    """Set context for tool execution"""
    _context["db"] = db
    _context["user_id"] = user_id

@tool
def add_task(title: str, list_name: str, description: Optional[str] = None, deadline: Optional[str] = None) -> str:
    """
    Add a new task to a specific list.
    
    Args:
        title: The task title
        list_name: Name of the list (e.g., "Town", "Home", "Free Time")
        description: Optional description with details
        deadline: Optional deadline in ISO format (e.g., "2024-01-15T10:00:00")
    
    Returns:
        Confirmation message
    """
    db = _context.get("db")
    user_id = _context.get("user_id")
    
    if not db or not user_id:
        return "Error: Context not set"
    
    # Find list by name
    from app.models import List as ListModel
    list_obj = db.query(ListModel).filter(
        ListModel.user_id == user_id,
        ListModel.name.ilike(list_name)  # Case-insensitive
    ).first()
    
    if not list_obj:
        # Create list if it doesn't exist
        list_obj = TaskService.create_list(db, user_id, ListCreate(name=list_name))
    
    # Create task
    task_data = TaskCreate(
        title=title,
        list_id=list_obj.id,
        description=description,
        deadline=deadline
    )
    
    task = TaskService.create_task(db, user_id, task_data)
    
    return f"✓ Added '{title}' to {list_name} list"

@tool
def create_list(name: str) -> str:
    """
    Create a new task list.
    
    Args:
        name: Name of the new list
    
    Returns:
        Confirmation message
    """
    db = _context.get("db")
    user_id = _context.get("user_id")
    
    if not db or not user_id:
        return "Error: Context not set"
    
    list_obj = TaskService.create_list(db, user_id, ListCreate(name=name))
    
    return f"✓ Created '{name}' list"

@tool
def get_today_context() -> str:
    """
    Get overview of today's tasks and lists.
    
    Returns:
        Summary of tasks organized by list
    """
    db = _context.get("db")
    user_id = _context.get("user_id")
    
    if not db or not user_id:
        return "Error: Context not set"
    
    # Get all lists and tasks
    lists = TaskService.get_user_lists(db, user_id)
    tasks = TaskService.get_user_tasks(db, user_id)
    
    if not tasks:
        return "You have no tasks yet. Ready to add some?"
    
    # Organize by list
    output = []
    for lst in lists:
        list_tasks = [t for t in tasks if t.list_id == lst.id]
        if list_tasks:
            pending = [t for t in list_tasks if not t.completed]
            output.append(f"\n**{lst.name}** ({len(pending)} pending):")
            for task in pending[:5]:  # Show max 5 per list
                output.append(f"  - {task.title}")
    
    return "\n".join(output) if output else "All tasks completed! 🎉"

# Export tools
tools = [add_task, create_list, get_today_context]