# Routes for the Admin Dashboard API and UI

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import secrets
from typing import List
import os

from . import db_manager, models, config

# Determine the base directory for templates relative to this file
template_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=template_dir)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    # Apply authentication dependency to all routes in this router
    dependencies=[Depends(db_manager.get_db)] # Add DB dependency globally for this router
)

security = HTTPBasic()

def get_current_admin_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Basic HTTP Authentication for admin routes."""
    correct_username = secrets.compare_digest(credentials.username, config.settings.ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, config.settings.ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    # In a real app, you might return a user object
    return credentials.username

# Apply authentication dependency to all routes requiring login
auth_dependency = Depends(get_current_admin_user)

# --- HTML Rendering Routes (UI) ---

@router.get("/", response_class=HTMLResponse, name="admin_home")
async def admin_home(request: Request, username: str = auth_dependency):
    """Renders the main admin dashboard page."""
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "username": username})

@router.get("/users-ui", response_class=HTMLResponse, name="list_users_html")
async def list_users_html(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(db_manager.get_db), username: str = auth_dependency):
    """Renders the user list page."""
    users = db.query(models.User).order_by(models.User.created_at.desc()).offset(skip).limit(limit).all()
    return templates.TemplateResponse("admin_users.html", {"request": request, "users": users, "username": username})

@router.get("/users-ui/{whatsapp_id}", response_class=HTMLResponse, name="get_user_details_html")
async def get_user_details_html(request: Request, whatsapp_id: str, db: Session = Depends(db_manager.get_db), username: str = auth_dependency):
    """Renders the user details page."""
    user = db_manager.get_user_by_whatsapp_id(db, whatsapp_id=whatsapp_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    messages = db_manager.get_user_messages(db, user_id=user.id, limit=50)
    wishlist_items = db_manager.get_wishlist_items(db, user_id=user.id)
    return templates.TemplateResponse("admin_user_details.html", {
        "request": request,
        "user": user,
        "messages": reversed(messages), # Show newest first in template if needed, or handle in template
        "wishlist_items": wishlist_items,
        "username": username
    })

# --- API Endpoints (Data for potential JS frontend or direct API access) ---
# These routes are kept separate from the HTML rendering routes

@router.get("/api/users", response_model=List[models.UserProfile], dependencies=[auth_dependency])
def list_users_api(skip: int = 0, limit: int = 100, db: Session = Depends(db_manager.get_db)):
    """API endpoint to list registered users."""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/api/users/{whatsapp_id}", response_model=models.UserProfile, dependencies=[auth_dependency])
def get_user_details_api(whatsapp_id: str, db: Session = Depends(db_manager.get_db)):
    """API endpoint to get details for a specific user by WhatsApp ID."""
    user = db_manager.get_user_by_whatsapp_id(db, whatsapp_id=whatsapp_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/api/users/{whatsapp_id}/messages", dependencies=[auth_dependency])
def get_user_conversation_api(whatsapp_id: str, limit: int = 50, db: Session = Depends(db_manager.get_db)):
    """API endpoint to get the recent conversation history for a specific user."""
    user = db_manager.get_user_by_whatsapp_id(db, whatsapp_id=whatsapp_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    messages = db_manager.get_user_messages(db, user_id=user.id, limit=limit)
    return [{"sender": msg.sender, "content": msg.content, "timestamp": msg.timestamp} for msg in reversed(messages)]

@router.get("/api/users/{whatsapp_id}/wishlist", response_model=List[models.WishlistItemResponse], dependencies=[auth_dependency])
def get_user_wishlist_api(whatsapp_id: str, db: Session = Depends(db_manager.get_db)):
    """API endpoint to get the wishlist items for a specific user."""
    user = db_manager.get_user_by_whatsapp_id(db, whatsapp_id=whatsapp_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    wishlist_items = db_manager.get_wishlist_items(db, user_id=user.id)
    return wishlist_items

# Add more admin API endpoints as needed

