# app/training/routes.py
from fastapi import APIRouter, Request, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from ..auth.utils import verify_token  # Using existing verify_token
import os

router = APIRouter()

@router.put("/acknowledge")
async def acknowledge_training(request: Request):
    # First verify token
    token_check = verify_token(request)
    if token_check:
        return token_check  # Returns redirect if not authenticated
    
    try:
        email = request.session["email"]
        client = AsyncIOMotorClient(os.getenv("MONGO_CON"))
        db = client.chatbot
        
        await db.users.update_one(
            {"email": email},
            {"$set": {"training_completed": True}}
        )
            
        return {"message": "Training completed"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))