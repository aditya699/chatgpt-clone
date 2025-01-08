#import
import time
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import os
from dotenv import load_dotenv
from urllib.parse import urlencode
import requests
from typing import Optional
from ..auth.utils import verify_token
# Load environment variables
load_dotenv()

# Initialize router
router = APIRouter()

#Azure AD Configuration
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"



# OAuth2 endpoints
AUTHORIZE_ENDPOINT = f"{AUTHORITY}/oauth2/v2.0/authorize"
TOKEN_ENDPOINT = f"{AUTHORITY}/oauth2/v2.0/token"
GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0/me"

@router.get("/login")
async def login(request: Request):
    """
    Redirect users to Azure AD login page
    """
    try:
        # Check for valid session first
        token_check = verify_token(request)
        if token_check is None:  # Valid session exists
            return RedirectResponse(url="/")
            
        # No valid session, proceed with Azure login
        auth_params = {
            "client_id": CLIENT_ID,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "response_mode": "query",
            "scope": "User.Read openid profile email",
            "state": "12345"  # Should be secure random in production
        }
        
        auth_url = f"{AUTHORIZE_ENDPOINT}?{urlencode(auth_params)}"
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
async def auth_callback(request: Request, code: Optional[str] = None, error: Optional[str] = None):
    """
    Handle the callback from Azure AD
    """
    try:
        if error:
            raise HTTPException(status_code=400, detail=f"Authentication error: {error}")
        
        if not code:
            raise HTTPException(status_code=400, detail="No authorization code received")

        # Exchange authorization code for tokens
        token_data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        # Get access token
        token_response = requests.post(TOKEN_ENDPOINT, data=token_data)
        token_response.raise_for_status()
        access_token = token_response.json().get("access_token")

        # Get user info from Microsoft Graph
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get(GRAPH_ENDPOINT, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()

        # Azure returns expires_in in seconds, convert to timestamp
        expires_at = time.time() + token_data.get("expires_in", 3600)  # Default 1 hour
         
        # Get username from user info
        display_name = user_info.get("displayName", "User")
        # Store both token and expiry
        request.session["user"] = display_name
        request.session["access_token"] = access_token
        request.session["token_expires_at"] = expires_at

        # Redirect to home route
        return RedirectResponse(url="/", status_code=303)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Microsoft: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))