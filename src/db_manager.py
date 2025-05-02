# Database session management and basic CRUD operations

from sqlalchemy.orm import Session
from sqlalchemy import update, func # Import func for server_default
from .models import Base, engine, SessionLocal, User, Message, WishlistItem
from .config import settings
from typing import List, Optional, Dict, Any

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes the database by creating tables."""
    print("Initializing database...")
    # In a real application, consider using Alembic for migrations
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables checked/created.")
    except Exception as e:
        print(f"ERROR initializing database: {e}")

# --- User CRUD Operations ---

def get_user_by_whatsapp_id(db: Session, whatsapp_id: str) -> User | None:
    """Retrieves a user by their WhatsApp ID."""
    return db.query(User).filter(User.whatsapp_id == whatsapp_id).first()

def create_user(db: Session, phone_number: str, whatsapp_id: str, profile_name: Optional[str] = None) -> User:
    """Creates a new user."""
    db_user = User(
        phone_number=phone_number,
        whatsapp_id=whatsapp_id,
        profile_name=profile_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print(f"Created user {db_user.id} for whatsapp_id {whatsapp_id}")
    return db_user

def update_user_profile(db: Session, whatsapp_id: str, profile_data: Dict[str, Any]) -> User | None:
    """Updates a user's profile information."""
    # Filter out keys that are not part of the User model's profile fields
    allowed_fields = ["profile_name", "style_preferences", "budget_range", "preferred_categories", "brand_preferences", "sizes", "shopping_context"]
    update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}

    if not update_data:
        print("No valid profile fields provided for update.")
        return get_user_by_whatsapp_id(db, whatsapp_id)

    try:
        stmt = update(User).where(User.whatsapp_id == whatsapp_id).values(**update_data)
        result = db.execute(stmt)
        db.commit()
        if result.rowcount > 0:
            print(f"Updated profile for user {whatsapp_id}")
            return get_user_by_whatsapp_id(db, whatsapp_id)
        else:
            print(f"User {whatsapp_id} not found for profile update.")
            return None
    except Exception as e:
        db.rollback()
        print(f"Error updating user profile for {whatsapp_id}: {e}")
        return None

# --- Message CRUD Operations ---

def create_message(db: Session, user_id: int, whatsapp_message_id: str, content: str, sender: str, metadata: Optional[Dict] = None) -> Message:
    """Creates a new message associated with a user."""
    db_message = Message(
        user_id=user_id,
        whatsapp_message_id=whatsapp_message_id,
        content=content,
        sender=sender,
        message_metadata=metadata
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_user_messages(db: Session, user_id: int, limit: int = 20) -> list[Message]:
    """Retrieves the latest messages for a given user."""
    return db.query(Message).filter(Message.user_id == user_id).order_by(Message.timestamp.desc()).limit(limit).all()

# --- Wishlist CRUD Operations ---

def add_to_wishlist(db: Session, user_id: int, item_data: Dict[str, Any]) -> WishlistItem:
    """Adds an item to the user's wishlist."""
    db_item = WishlistItem(
        user_id=user_id,
        product_id=item_data.get("product_id"),
        product_name=item_data.get("product_name"),
        product_url=item_data.get("product_url"),
        product_image_url=item_data.get("product_image_url"),
        notes=item_data.get("notes")
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    print(f"Added item {db_item.id} to wishlist for user {user_id}")
    return db_item

def get_wishlist_items(db: Session, user_id: int) -> List[WishlistItem]:
    """Retrieves all items from the user's wishlist."""
    return db.query(WishlistItem).filter(WishlistItem.user_id == user_id).order_by(WishlistItem.added_at.desc()).all()

def remove_from_wishlist(db: Session, user_id: int, item_id: int) -> bool:
    """Removes an item from the user's wishlist by its ID."""
    db_item = db.query(WishlistItem).filter(WishlistItem.id == item_id, WishlistItem.user_id == user_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        print(f"Removed item {item_id} from wishlist for user {user_id}")
        return True
    print(f"Item {item_id} not found in wishlist for user {user_id}")
    return False

# Add more CRUD operations as needed

# Allow running this script directly to initialize the database
if __name__ == "__main__":
    init_db()

