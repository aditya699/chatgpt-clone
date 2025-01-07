from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    azure_id = Column(String, unique=True)
    last_login = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="user")

    chat_sessions = relationship("ChatSession", back_populates="user")


    def __init__(self, email: str, name: str = None, azure_id: str = None):
        self.email = email
        self.name = name
        self.azure_id = azure_id
        self.last_login = datetime.utcnow()

    def update_last_login(self):
        self.last_login = datetime.utcnow()


