import time
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse


def verify_token(request: Request):
    """
    Verify session has valid user and non-expired token
    """
    session = request.session
    
    # Check if both user and token exist
    if not all(key in session for key in ["user", "access_token", "token_expires_at"]):
        return RedirectResponse(url="/auth/login", status_code=303)
    
    # Check if token is expired
    if time.time() >= session["token_expires_at"]:
        session.clear()  # Clear invalid session
        return RedirectResponse(url="/auth/login", status_code=303)
    
    return None  # All checks passed