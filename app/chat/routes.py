from fastapi import APIRouter, Request, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from ..auth.utils import verify_token
import os
from datetime import datetime
from bson import ObjectId  # Add this import

from pydantic import BaseModel

# Create a model for the message
class ChatMessage(BaseModel):
    session_id: str
    message: str

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

@router.post("/message")
async def send_message(
    request: Request,
    chat_message: ChatMessage
):
    """
    Handle sending a message in a specific chat session
    """
    try:
        # Verify token
        token_check = verify_token(request)
        if token_check is not None:
            return token_check
        
        # Get user email from session
        email = request.session.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="No email found in session")
        
        # Create message document
        message_doc = {
            "session_id": chat_message.session_id,
            "role": "user",
            "content": chat_message.message,
            "timestamp": datetime.utcnow()
        }
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(os.getenv("MONGO_CON"))
        db = client.chatbot
        
        # Convert string ID to ObjectId
        session_object_id = ObjectId(chat_message.session_id)
        
        # Add message to session
        result = await db.chat_sessions.update_one(
            {"_id": session_object_id, "email": email},
            {"$push": {"messages": message_doc}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # For now, just echo the message back
        assistant_response = {
            "session_id": chat_message.session_id,
            "role": "assistant",
            "content": f"Echo: {chat_message.message}",
            "timestamp": datetime.utcnow()
        }
        
        # Store assistant's response
        await db.chat_sessions.update_one(
            {"_id": session_object_id, "email": email},
            {"$push": {"messages": assistant_response}}
        )
        
        return {
            "message": "Message sent successfully",
            "response": assistant_response["content"]
        }
        
    except Exception as e:
        print(f"Error in send_message: {str(e)}")  # Add debug print
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get-user-sessions")
async def get_user_sessions(
    request: Request,
    page: int = 1,
    limit: int = 10
):
    try:
        # Verify token
        token_check = verify_token(request)
        if token_check is not None:
            return token_check
        
        # Get user email from session
        email = request.session.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="No email found in session")
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(os.getenv("MONGO_CON"))
        db = client.chatbot
        
        # Calculate skip for pagination
        skip = (page - 1) * limit
        
        # Get total count for pagination
        total_sessions = await db.chat_sessions.count_documents({"email": email})
        
        # Fetch sessions with pagination and sorting
        cursor = db.chat_sessions.find(
            {"email": email}
        ).sort(
            "updated_at", -1  # Sort by most recent first
        ).skip(skip).limit(limit)
        
        # Convert cursor to list and format the response
        sessions = []
        async for session in cursor:
            messages = []
            for msg in session.get("messages", []):
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg["timestamp"]
                })
            
            sessions.append({
                "session_id": str(session["_id"]),
                "created_at": session["created_at"],
                "updated_at": session["updated_at"],
                "messages": messages,
                "message_count": len(session["messages"])
            })
        
        return {
            "sessions": sessions,
            "total": total_sessions,
            "page": page,
            "total_pages": (total_sessions + limit - 1) // limit
        }
        
    except Exception as e:
        print(f"Error in get_user_sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))