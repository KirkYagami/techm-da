"""
Module doc strings 
"""
from middleware import log_requests
from fastapi import FastAPI


app = FastAPI()

app.middleware("http")(log_requests)

@app.get('/')
def index():
    """
    Just for homepage... returns just a string!
    """
    return "Index Page!"

@app.get('/movies')
def movies():
    return {"m1": "Dhurandhar", "m2":"RRR", "m3":"Darling"}

@app.get("/users/{id}/posts")
def user_posts(id:int):
    return f"Posts page for user: {id}"


# uvicorn

@app.get("/items")
async def read_items(
    skip: int = 0,     # optional, default = 0
    limit: int = 10,   # optional, default = 10
    q: str | None = None  # optional, can be absent
):
    # GET /items?skip=5&limit=3&q=hammer
    return {"skip": skip, "limit": limit, "q": q}

@app.get("/users/{id}/events")
def read_user_events(id, limit=0, q=""):
    return f"Events page"


from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id:int
    username:str
    email:EmailStr

from pydantic import BaseModel
from typing import Optional

# ① Define the shape of your request body
class Item(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    in_stock: bool = True

# ② FastAPI reads the body and gives you a typed object
@app.post("/items")
async def create_item(item: Item):  # ← body declared as type hint
    return {"itemName": item.name, "price": item.price}
