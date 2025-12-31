from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
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
    response = chat_with_mentor(chat_msg.message, db, current_user.id)
    return {"response": response}