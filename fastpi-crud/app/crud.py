# app/crud.py

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from app import models, schemas


# ================================================================
# READ OPERATIONS
# ================================================================

def get_item(db: Session, item_id: int) -> Optional[models.Item]:
    """
    Fetch a single item by its primary key.
    Returns None if not found (we handle 404 in the router).
    """
    return db.query(models.Item).filter(models.Item.id == item_id).first()
    # .query(models.Item) → SELECT * FROM items
    # .filter(...)        → WHERE id = item_id
    # .first()            → LIMIT 1, returns object or None


def get_items(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    available_only: bool = False
) -> List[models.Item]:
    """
    Fetch a paginated list of items.
    skip/limit implement pagination: skip=20, limit=10 → page 3 of 10.
    """
    query = db.query(models.Item)
    
    # Conditionally add a filter
    if available_only:
        query = query.filter(models.Item.is_available == True)
    
    return query.offset(skip).limit(limit).all()
    # .offset(skip) → OFFSET 0
    # .limit(limit) → LIMIT 100
    # .all()        → returns a list (empty list if no results)


def get_item_by_name(db: Session, name: str) -> Optional[models.Item]:
    """Check if an item with a given name already exists."""
    return db.query(models.Item).filter(models.Item.name == name).first()


# ================================================================
# CREATE OPERATION
# ================================================================

def create_item(db: Session, item: schemas.ItemCreate) -> models.Item:
    """
    Insert a new item into the database.
    
    Flow:
    1. Create an ORM object from the Pydantic schema
    2. Add to session (stages the INSERT)
    3. Commit (sends INSERT to DB)
    4. Refresh (reload from DB to get auto-generated fields like id)
    """
    # Convert Pydantic schema → SQLAlchemy model instance
    # item.model_dump() returns a plain dict: {"name": "...", "price": 9.99, ...}
    db_item = models.Item(**item.model_dump())
    
    db.add(db_item)     # Stage: adds object to session's "pending" list
    db.commit()         # Execute: sends INSERT to MySQL
    db.refresh(db_item) # Sync: reload from DB (gets id, created_at, etc.)
    
    return db_item


# ================================================================
# UPDATE OPERATION
# ================================================================

def update_item(
    db: Session, 
    item_id: int, 
    item_update: schemas.ItemUpdate
) -> Optional[models.Item]:
    """
    Partially update an item (PATCH semantics).
    Only updates fields that are explicitly provided (not None).
    """
    # First, find the existing record
    db_item = get_item(db, item_id)
    if db_item is None:
        return None
    
    # model_dump(exclude_unset=True) only returns fields the CLIENT sent.
    # If client sent {"price": 19.99}, we only update price — not name, etc.
    update_data = item_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_item, field, value)
        # setattr(db_item, "price", 19.99) ← equivalent to db_item.price = 19.99
    
    db.commit()         # Execute UPDATE
    db.refresh(db_item) # Sync updated_at, etc.
    
    return db_item


# ================================================================
# DELETE OPERATION
# ================================================================

def delete_item(db: Session, item_id: int) -> bool:
    """
    Delete an item by id.
    Returns True if deleted, False if item was not found.
    """
    db_item = get_item(db, item_id)
    if db_item is None:
        return False
    
    db.delete(db_item)  # Stage: marks object for deletion
    db.commit()         # Execute: sends DELETE to MySQL
    
    return True