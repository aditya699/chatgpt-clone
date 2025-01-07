# app/chat/routes.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.auth import get_current_user, is_authenticated
from app.database import get_db
from app.chat import crud
chat_router = APIRouter()

@chat_router.post("/sessions/{session_id}/message")  # Changed from /echo to better match REST conventions
async def send_message(
    request: Request,
    session_id: int,
    message: str,
    db: Session = Depends(get_db)
):
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_current_user(request)
    
    # Verify chat session exists and belongs to user
    chat_session = crud.get_chat_session(db, session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if chat_session.user_id != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to access this chat session")
    
    # Create the message
    db_message = crud.create_message(
        db=db,
        user_id=user['id'],
        session_id=session_id,
        content=message,
        response=f"Echo: {message}"
    )
    
    return {
        "session_id": session_id,
        "message": db_message.content,
        "response": db_message.response,
        "timestamp": db_message.timestamp
    }
@chat_router.post("/sessions/new")
async def create_session(
    request: Request,
    title: str = "New Chat",
    db: Session = Depends(get_db)
):
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_current_user(request)
    
    # Create new chat session
    chat_session = crud.create_chat_session(
        db=db,
        user_id=user['id'],
        title=title
    )
    
    return {
        "session_id": chat_session.id,
        "title": chat_session.title,
        "created_at": chat_session.created_at
    }

@chat_router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    request: Request,
    session_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = get_current_user(request)
    
    # Verify chat session exists and belongs to user
    chat_session = crud.get_chat_session(db, session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if chat_session.user_id != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to access this chat session")
    
    # Get messages for this session
    messages = crud.get_session_messages(db, session_id, skip=skip, limit=limit)
    
    return {
        "session_id": session_id,
        "messages": messages
    }