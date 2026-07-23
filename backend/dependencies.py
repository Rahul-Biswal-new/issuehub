from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db
import models
from auth_utils import decode_access_token

# Helper to extract token from Header or Cookie
def get_token(request: Request) -> str:
    # 1. Check Authorization Header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    
    # 2. Check Cookie
    token_cookie = request.cookies.get("access_token")
    if token_cookie:
        return token_cookie
        
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Not authenticated. Missing token in header or cookie."
            }
        }
    )

def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)) -> models.User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Could not validate credentials or token expired."
                }
            }
        )
    
    email: str = payload.get("email")
    sub: str = payload.get("sub")
    if not email or not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Token is missing sub/email payload."
                }
            }
        )
    try:
        user_id = int(sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Token sub claim is not a valid user ID."
                }
            }
        )
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "User associated with this token does not exist."
                }
            }
        )
    return user


def get_member(db: Session, project_id: int, user_id: int):
    """Return the ProjectMember row or None. Shared by issues & comments routers."""
    return (
        db.query(models.ProjectMember)
        .filter(
            models.ProjectMember.project_id == project_id,
            models.ProjectMember.user_id == user_id,
        )
        .first()
    )
