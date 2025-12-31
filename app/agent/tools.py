from langchain_core.tools import tool
from typing import Optional
from uuid import UUID
from app.services.entity_service import EntityService
from app.schemas.entity import EntityCreate

# Global context
_context = {}

def set_agent_context(db, user_id: UUID):
    _context["db"] = db
    _context["user_id"] = user_id

@tool
def add_entity(
    title: str, 
    entity_type: str,
    context_tags: list[str],
    description: Optional[str] = None,
    due_at: Optional[str] = None
) -> str:
    """
    Add a new entity (task, event, etc.)
    
    Args:
        title: The title
        entity_type: 'task' or 'event'
        context_tags: List like ['town', 'work', 'personal']
        description: Optional details
        due_at: Optional deadline
    """
    db = _context.get("db")
    user_id = _context.get("user_id")
    
    if not db or not user_id:
        return "Error: Context not set"
    
    entity_data = EntityCreate(
        entity_type=entity_type,
        title=title,
        description=description,
        due_at=due_at,
        context_tags=context_tags
    )
    
    entity = EntityService.create_entity(db, user_id, entity_data)
    
    tags_str = ", ".join(context_tags)
    return f"✓ Added '{title}' ({entity_type}) with context: {tags_str}"

@tool
def get_entities_overview() -> str:
    """Get overview of all entities"""
    db = _context.get("db")
    user_id = _context.get("user_id")
    
    if not db or not user_id:
        return "Error: Context not set"
    
    entities = EntityService.get_user_entities(db, user_id, status="pending")
    
    if not entities:
        return "You have no pending entities yet."
    
    # Group by context
    by_context = {}
    for e in entities:
        for tag in e.context_tags or ['untagged']:
            if tag not in by_context:
                by_context[tag] = []
            by_context[tag].append(e)
    
    output = []
    for context, ents in by_context.items():
        output.append(f"\n**{context.upper()}** ({len(ents)} items):")
        for e in ents[:5]:
            output.append(f"  - {e.title}")
    
    return "\n".join(output)

# Export
tools = [add_entity, get_entities_overview]