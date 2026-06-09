# app/schemas.py

from pydantic import BaseModel, Field
from typing import Optional

# ------------------------------------------------------------------
# BASE SCHEMA
# Shared fields that appear in multiple schemas
# ------------------------------------------------------------------
class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, 
                      description="Name of the item")
    description: Optional[str] = Field(None, max_length=500,
                                       description="Optional description")
    price: float = Field(..., gt=0, description="Price must be positive")
    is_available: bool = True

# ------------------------------------------------------------------
# CREATE SCHEMA
# Used when a client SENDS data to create a new item (POST request).
# Does NOT include 'id' because the DB generates it.
# ------------------------------------------------------------------
class ItemCreate(ItemBase):
    pass  # Inherits all fields from ItemBase — nothing extra needed

# ------------------------------------------------------------------
# UPDATE SCHEMA
# Used for partial updates (PATCH). All fields are Optional —
# the client only needs to send what they want to change.
# ------------------------------------------------------------------
class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None

# ------------------------------------------------------------------
# RESPONSE SCHEMA
# What we SEND BACK to the client. Includes 'id' from the database.
# ------------------------------------------------------------------
class ItemResponse(ItemBase):
    id: int
    
    # This tells Pydantic to read data from SQLAlchemy ORM objects
    # (not just plain dicts). Without this, ORM objects won't serialize.
    class Config:
        from_attributes = True  # Pydantic v2 (use orm_mode = True for v1)