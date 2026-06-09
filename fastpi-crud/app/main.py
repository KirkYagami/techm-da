# app/main.py  (updated)

from fastapi import FastAPI
from app.database import engine, Base
from app.routers import items

# Create all tables defined in models.py if they don't exist yet.
# In production, use Alembic migrations instead (see Section 9).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Items CRUD API",
    description="A production-ready CRUD API with MySQL",
    version="1.0.0"
)

# Include the items router — registers all /items routes
app.include_router(items.router)

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "API is running"}