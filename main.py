from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from app.auth.route import router as auth_router
import uvicorn
import os
from dotenv import load_dotenv
from app.auth.utils import verify_token

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="ChatBot Service", version="1.0.0")

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
    session_cookie="chatbot_session",
    max_age=1800  # 30 minutes
)

# Configure CORS
origins = ["*"]  # Allow all origins for development

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

#Root endpoint
@app.get("/")
async def root(request: Request):
    # Verify token first
    token_check = verify_token(request)
    if token_check:
        return token_check  # This will be the redirect response
    
    session = request.session
    return {
        "message": f"Welcome back, {session['user']}!",
        "status": "ChatBot Service API is running",
        "Welcome Message":"The developer is trying his best to bring this up"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)