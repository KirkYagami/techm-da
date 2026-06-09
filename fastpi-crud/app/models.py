# app/models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func
from app.database import Base

class Item(Base):
    # The actual table name in MySQL
    __tablename__ = "items"

    # --- Columns ---
    id = Column(
        Integer, 
        primary_key=True,   # This is the PK
        index=True,         # Creates a DB index for fast lookups
        autoincrement=True  # MySQL auto-increments this
    )
    name = Column(
        String(100),        # VARCHAR(100) in MySQL
        nullable=False,     # NOT NULL constraint
        index=True          # Index for fast name searches
    )
    description = Column(
        String(500), 
        nullable=True       # This column can be NULL
    )
    price = Column(
        Float, 
        nullable=False
    )
    is_available = Column(
        Boolean, 
        default=True,       # Default value when not provided
        nullable=False
    )
    created_at = Column(
        DateTime,
        server_default=func.now()   # MySQL sets this automatically on INSERT
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()         # MySQL updates this automatically on UPDATE
    )
    category = Column(String(50), nullable=True)   # ← NEW

    # String representation — useful for debugging
    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', price={self.price})>"