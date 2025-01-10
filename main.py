from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from app.auth.route import router as auth_router
import uvicorn
import os
from dotenv import load_dotenv
from app.auth.utils import verify_token,update_user_last_login
from app.training.routes import router as training_router
from app.chat.routes import router as chat_router  

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
app.include_router(training_router, prefix="/training", tags=["Training"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])  

#Root endpoint
@app.get("/")
async def root(request: Request):
    try:
        # Verify token first
        token_check = verify_token(request)
        if token_check:
            return token_check
        
        session = request.session
        return {
            "message": f"Welcome back, {session['user']}!",
            "status": "success"
        }
    except Exception as e:
        print(f"Error in root route: {str(e)}")  # Add this for debugging
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)