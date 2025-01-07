from fastapi import   FastAPI,APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi.middleware.cors import CORSMiddleware
from app.auth.auth import auth_router, is_authenticated
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
from dotenv import load_dotenv
from app import init_db
import os
from app.auth.auth import get_current_user
from app.chat import crud
from app.chat.routes import chat_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI()

# Initialize database
init_db()

# Fetch the secret key from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")

# Set up session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the authentication router
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

app.include_router(chat_router, prefix="/chat", tags=["chat"])


@app.get("/")
async def read_root(request: Request, db: Session = Depends(get_db)):
    if not is_authenticated(request):
        return RedirectResponse(url="/auth/login")
    
    user = get_current_user(request)
    
    # Get all chat sessions for this user
    user_sessions = crud.get_user_chat_sessions(db, user['id'])
    
    return {
        "user": user,
        "sessions": [
            {
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at,
                "last_updated": session.last_updated
            }
            for session in user_sessions
        ]
    }