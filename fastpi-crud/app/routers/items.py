# app/routers/items.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, schemas
from app.database import get_db

# APIRouter is like a mini FastAPI app — groups related routes.
# We include this in main.py with a prefix and tags.
router = APIRouter(
    prefix="/items",     # All routes here start with /items
    tags=["Items"],      # Groups routes under "Items" in Swagger docs
)


# ================================================================
# GET /items — List all items (with pagination)
# ================================================================
@router.get("/", response_model=List[schemas.ItemResponse])
def read_items(
    skip: int = Query(default=0, ge=0, description="Number of items to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Max items to return"),
    available_only: bool = Query(default=False),
    db: Session = Depends(get_db)
    # ↑ Depends(get_db) tells FastAPI: 
    #   "Call get_db(), inject the yielded session here, 
    #    and clean it up after this function returns."
):
    """Retrieve a paginated list of items."""
    items = crud.get_items(db, skip=skip, limit=limit, available_only=available_only)
    return items


# ================================================================
# GET /items/{item_id} — Get a single item
# ================================================================
@router.get("/{item_id}", response_model=schemas.ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single item by its ID.
    FastAPI automatically parses {item_id} from the URL as an int.
    """
    db_item = crud.get_item(db, item_id=item_id)
    
    if db_item is None:
        # HTTPException → FastAPI returns JSON: {"detail": "Item not found"}
        # with HTTP 404 status code
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return db_item


# ================================================================
# POST /items — Create a new item
# ================================================================
@router.post("/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """
    Create a new item.
    FastAPI reads the request body, validates it with ItemCreate schema,
    and passes a clean Python object to this function.
    """
    # Business rule: item names must be unique
    existing = crud.get_item_by_name(db, name=item.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An item named '{item.name}' already exists"
        )
    
    return crud.create_item(db=db, item=item)


# ================================================================
# PATCH /items/{item_id} — Partially update an item
# ================================================================
@router.patch("/{item_id}", response_model=schemas.ItemResponse)
def update_item(
    item_id: int, 
    item: schemas.ItemUpdate, 
    db: Session = Depends(get_db)
):
    """
    Partially update an item. Only provided fields are changed.
    PATCH is preferred over PUT for partial updates.
    """
    updated_item = crud.update_item(db=db, item_id=item_id, item_update=item)
    
    if updated_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return updated_item


# ================================================================
# DELETE /items/{item_id} — Delete an item
# ================================================================
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """
    Delete an item. Returns 204 No Content on success.
    204 means "success but nothing to send back."
    """
    success = crud.delete_item(db=db, item_id=item_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    # Returning None with status_code=204 is correct — no body needed