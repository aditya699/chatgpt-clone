from fastapi import APIRouter, Request, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from ..auth.utils import verify_token
import os
from datetime import datetime

# Initialize router
router = APIRouter()

@router.post("/create-session")
async def create_chat_session(request: Request):
    """
    Create a new chat session for the user
    """
    try:
        # First verify token
        token_check = verify_token(request)
        if token_check is not None:  # Important: check for None, not just if token_check
            return token_check
        
        print("Token verification passed")
        
        # Get user email from session
        email = request.session.get("email")
        print("Got email from session:", email)
        
        if not email:
            raise HTTPException(status_code=400, detail="No email found in session")
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(os.getenv("MONGO_CON"))
        db = client.chatbot
        
        # Create new session document
        new_session = {
            "email": email,
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "active"
        }
        
        print("Creating new session:", new_session)
        
        # Insert into database
        result = await db.chat_sessions.insert_one(new_session)
        
        print("Session created with ID:", result.inserted_id)
        
        return {
            "message": "Chat session created successfully",
            "session_id": str(result.inserted_id)
        }
        
    except Exception as e:
        print("Error in create_chat_session:", str(e))
        raise HTTPException(status_code=500, detail=str(e))