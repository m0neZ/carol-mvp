# Pydantic models for API requests/responses and SQLAlchemy models for database

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func
from .config import settings # Import settings to get DATABASE_URL

# --- SQLAlchemy Setup ---

# Check if DATABASE_URL is set, otherwise use a default SQLite for local dev/testing
if settings.DATABASE_URL and settings.DATABASE_URL.startswith("postgresql"):
    print(f'Using PostgreSQL database: {settings.DATABASE_URL.split("@")[1]}') # Avoid logging credentials
    engine = create_engine(settings.DATABASE_URL)
elif settings.DATABASE_URL and settings.DATABASE_URL.startswith("sqlite"):
    print(f"Using SQLite database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
else:
    db_path = "./shoppergpt.db"
    print(f"WARNING: DATABASE_URL not configured correctly. Using default local SQLite DB: {db_path}")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQLAlchemy Models ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    whatsapp_id = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    profile_name = Column(String, nullable=True) # Store the name from WhatsApp profile
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Enhanced Profile Fields
    style_preferences = Column(Text, nullable=True) # Free text or structured tags
    budget_range = Column(String, nullable=True) # e.g., "$50-$100", "under $50"
    preferred_categories = Column(JSON, nullable=True) # e.g., ["electronics", "mens_fashion"]
    brand_preferences = Column(JSON, nullable=True) # e.g., ["Nike", "Apple"]
    sizes = Column(JSON, nullable=True) # e.g., {"shirt": "M", "shoes": "10"}
    shopping_context = Column(JSON, nullable=True) # Store inferred context like location, upcoming events from calendar (future)

    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="user", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whatsapp_message_id = Column(String, index=True) # Not always unique if AI message ID is placeholder
    content = Column(Text, nullable=False)
    sender = Column(String, nullable=False) # 'user' or 'assistant'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    # Add metadata if needed, e.g., message type, media URL
    message_metadata = Column(JSON, nullable=True)

    user = relationship("User", back_populates="messages")

class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(String) # ID from affiliate platform or internal catalog
    product_name = Column(String, nullable=False)
    product_url = Column(String)
    product_image_url = Column(String, nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
    # Add price tracking fields if needed (current_price, target_price)

    user = relationship("User", back_populates="wishlist_items")

# Add other models as needed (e.g., Products cache, AdminUser)

# --- Pydantic Models ---

class WhatsAppMessageValue(BaseModel):
    messaging_product: str
    metadata: dict
    contacts: Optional[List[dict]] = None
    errors: Optional[List[dict]] = None
    messages: Optional[List[dict]] = None
    statuses: Optional[List[dict]] = None

class WhatsAppMessageEntry(BaseModel):
    id: str
    changes: List[WhatsAppMessageValue]

class WhatsAppWebhookPayload(BaseModel):
    object: str
    entry: List[WhatsAppMessageEntry]

# Pydantic model for User Profile (used for API responses/updates)
class UserProfile(BaseModel):
    whatsapp_id: str
    phone_number: str
    profile_name: Optional[str] = None
    style_preferences: Optional[str] = None
    budget_range: Optional[str] = None
    preferred_categories: Optional[List[str]] = None
    brand_preferences: Optional[List[str]] = None
    sizes: Optional[Dict[str, str]] = None
    created_at: Optional[Any] = None # Use Any for datetime flexibility
    updated_at: Optional[Any] = None

    class Config:
        from_attributes = True # Replaces orm_mode in Pydantic v2

# Pydantic model for Wishlist Item
class WishlistItemBase(BaseModel):
    product_id: str
    product_name: str
    product_url: Optional[str] = None
    product_image_url: Optional[str] = None
    notes: Optional[str] = None

class WishlistItemCreate(WishlistItemBase):
    pass

class WishlistItemResponse(WishlistItemBase):
    id: int
    user_id: int
    added_at: Any

    class Config:
        from_attributes = True

# Add more Pydantic models for API interactions

