import time
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
import requests

def verify_token(request: Request):
    """
    Verify session has valid user and non-expired token
    """
    session = request.session
    
    # Check if all required session data exists
    required_keys = ["user", "email", "access_token", "token_expires_at"]
    if not all(key in session for key in required_keys):
        return RedirectResponse(url="/auth/login", status_code=303)
    
    # Check if token is expired
    if time.time() >= session["token_expires_at"]:
        session.clear()  # Clear invalid session
        return RedirectResponse(url="/auth/login", status_code=303)
    
    return None  # All checks passed

async def update_user_last_login(request: Request):
    """
    Update user's last login time in database using session email
    """
    try:
        # Get email directly from session
        email = request.session["email"]
        
        # Update last login
        client = AsyncIOMotorClient(os.getenv("MONGO_CON"))
        db = client.chatbot
        
        await db.users.update_one(
            {"email": email},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        return True
    except Exception as e:
        print(f"Error updating last login: {str(e)}")
        return False