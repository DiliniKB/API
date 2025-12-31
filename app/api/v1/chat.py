from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Message
from app.auth import get_current_user
from app.schemas.chat import ChatMessage, ChatResponse
from app.agent.mentor import chat_with_mentor

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
def send_message(
    chat_msg: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to the mentor agent"""
    
    # Store user message
    user_message = Message(
        user_id=current_user.id,
        role="user",
        content=chat_msg.message
    )
    db.add(user_message)
    db.commit()
    
    # Get response from agent
    response = chat_with_mentor(chat_msg.message, db, current_user.id)
    
    # Store assistant message
    assistant_message = Message(
        user_id=current_user.id,
        role="assistant",
        content=response
    )
    db.add(assistant_message)
    db.commit()
    
    return {"response": response}

@router.get("/history")
def get_chat_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation history"""
    messages = db.query(Message).filter(
        Message.user_id == current_user.id
    ).order_by(Message.created_at.desc()).limit(limit).all()
    
    return {"messages": list(reversed(messages))}

@router.delete("/history")
def clear_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear conversation history (but keep entities)"""
    db.query(Message).filter(Message.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Chat history cleared"}