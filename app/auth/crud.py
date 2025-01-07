from sqlalchemy.orm import Session
from . import models
from datetime import datetime

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_azure_id(db: Session, azure_id: str):
    return db.query(models.User).filter(models.User.azure_id == azure_id).first()

def create_user(db: Session, email: str, name: str = None, azure_id: str = None):
    db_user = models.User(
        email=email,
        name=name,
        azure_id=azure_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_login(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
    return db_user

def create_or_update_user(db: Session, email: str, name: str = None, azure_id: str = None):
    # Try to find user by email
    db_user = get_user_by_email(db, email)
    
    if db_user:
        # Update existing user
        db_user.name = name if name else db_user.name
        db_user.azure_id = azure_id if azure_id else db_user.azure_id
        db_user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(db_user)
    else:
        # Create new user
        db_user = create_user(db, email, name, azure_id)
    
    return db_user