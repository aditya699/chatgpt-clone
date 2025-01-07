# app/chat/crud.py
from sqlalchemy.orm import Session
from . import models
from typing import List

def create_message(db: Session, user_id: int, content: str, response: str):
    db_message = models.Message(
        user_id=user_id,
        content=content,
        response=response
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_user_messages(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Message)\
        .filter(models.Message.user_id == user_id)\
        .order_by(models.Message.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_message(db: Session, message_id: int):
    return db.query(models.Message)\
        .filter(models.Message.id == message_id)\
        .first()

def get_user_chat_sessions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all chat sessions for a user"""
    return db.query(models.ChatSession)\
        .filter(models.ChatSession.user_id == user_id)\
        .order_by(models.ChatSession.last_updated.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_chat_session(db: Session, user_id: int, title: str = "New Chat"):
    """Create a new chat session"""
    db_session = models.ChatSession(
        user_id=user_id,
        title=title
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_chat_session(db: Session, session_id: int):
    """Get a specific chat session"""
    return db.query(models.ChatSession)\
        .filter(models.ChatSession.id == session_id)\
        .first()

def get_session_messages(db: Session, session_id: int, skip: int = 0, limit: int = 50):
    return db.query(models.Message)\
        .filter(models.Message.session_id == session_id)\
        .order_by(models.Message.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()