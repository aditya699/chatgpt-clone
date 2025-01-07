# app/auth/auth.py
'''
NOTE:
1. OAuth Integration (from authlib.integrations.starlette_client import OAuth):
   - Handles OAuth authentication flows 
   - Works with various providers (Azure AD, Google, etc.)
   - Manages redirects, responses, token exchanges

2. OAuth Instance (oauth = OAuth()):
   - Manages connection to Azure AD
   - Handles redirects and token exchanges
   - One instance can handle multiple providers

3. OAuth2 Protocol:
   - Industry standard for authentication
   - User never shares password with your app
   - Flow: Your App → Microsoft Login → Back to Your App with token

4. Azure AD (Active Directory):
   - Microsoft's identity service
   - Manages users and permissions
   - Your app uses it as identity provider

5. Session Management:
   - SessionMiddleware handles all session operations
   - Flow: 
     a. User logs in via Microsoft
     b. Your app gets user info
     c. Stores in session (request.session['user'] = {...})
     d. SessionMiddleware encrypts and creates cookie
     e. Browser stores cookie
     f. Cookie sent with every request

6. Login Flow Details:
   a. User visits /auth/login
   b. Redirected to Microsoft
   c. After login, Microsoft sends code to /callback
   d. /callback exchanges code for tokens
   e. User info stored in session
   f. Redirect to home page

7. Security Features (Handled by SessionMiddleware):
   - Automatic encryption/decryption
   - Secure cookie management
   - Token validation
   - Session expiration
   - No manual JWT handling needed

8. Helper Functions:
   is_authenticated(): Checks if user has valid session
   get_current_user(): Gets user info from session

'''
#Necessary Import
#region Imports
from fastapi import APIRouter, Request, HTTPException, Depends
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
from typing import Optional
from sqlalchemy.orm import Session
import json
from app.database import get_db
from . import crud


#region Configuration
#Load environment variables from .env file
config = Config(".env")
CLIENT_ID = config("CLIENT_ID")
CLIENT_SECRET = config("CLIENT_SECRET")
TENANT_ID = config("TENANT_ID")
REDIRECT_URI = config("REDIRECT_URI")

#region OAuth Setup
# Initialize OAuth client for handling authentication
oauth = OAuth()

# Configure Azure AD OAuth provider with necessary endpoints and credentials
oauth.register(
    name="azure",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url=f'https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration',
    authorize_url=f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize",
    authorize_params=None,
    access_token_url=f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
    client_kwargs={"scope": "openid profile email"}
)

# Create FastAPI router for auth endpoints
auth_router = APIRouter()
#endregion

#region Authentication Routes
# Login endpoint - redirects user to Azure AD login page
@auth_router.get("/login")
async def login(request: Request):
    # First check if user is already authenticated
    if is_authenticated(request):
        return RedirectResponse(url='/')
        
    redirect_uri = REDIRECT_URI
    return await oauth.azure.authorize_redirect(
        request, 
        redirect_uri,
        prompt='login'
    )

# Callback endpoint - handles the response from Azure AD after successful login
@auth_router.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        # Exchange authorization code for access token
        token = await oauth.azure.authorize_access_token(request)
        if not token:
            raise HTTPException(status_code=400, detail="Failed to get access token")

        # Extract user information from token
        user = token.get('userinfo')
   
        if not user:
            # Fallback to ID token if userinfo is not available
            id_token = token.get('id_token')
            if id_token:
                claims = json.loads(
                    json.dumps(token.get('id_token_claims', {}))
                )
                user = {
                    'email': claims.get('email', ''),
                    'name': claims.get('name', ''),
                    'preferred_username': claims.get('preferred_username', ''),
                    'sub': claims.get('sub', '')  # Azure AD unique identifier
                }
            else:
                raise HTTPException(status_code=400, detail="No user info available")

        # Persist user data in database
        db_user = crud.create_or_update_user(
            db=db,
            email=user.get('email', user.get('preferred_username', '')),
            name=user.get('name', ''),
            azure_id=user.get('sub', '')
        )
        
        # Store user session data
        request.session['user'] = {
            'email': db_user.email,
            'name': db_user.name,
            'id': db_user.id,
            'access_token': token.get('access_token'),
            'token_type': token.get('token_type', 'Bearer')
        }

        return RedirectResponse(url='/')
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
#endregion

#region Helper Functions
# Authentication check helper
def is_authenticated(request: Request) -> bool:
    return 'user' in request.session

# Current user helper
def get_current_user(request: Request) -> Optional[dict]:
    return request.session.get('user')
#endregion

