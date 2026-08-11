# ==========================================
# File: routers/store.py
# Description: API routes for Gamification Store (Themes, Avatars)
# Author: AI Agent
# Created: 2026-08-02
# ==========================================

from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

router = APIRouter(
    prefix="/store",
    tags=["store"]
)

class StoreItem(BaseModel):
    id: int
    name: str
    description: str
    price_coins: int
    item_type: str # "theme", "avatar", "badge"

# Mock Database for store items
STORE_ITEMS = [
    StoreItem(id=1, name="Hacker Dark Theme", description="A cool neon green on black theme.", price_coins=500, item_type="theme"),
    StoreItem(id=2, name="Pro Developer Avatar", description="Exclusive avatar border.", price_coins=250, item_type="avatar"),
    StoreItem(id=3, name="Golden Code Badge", description="Show off your wealth.", price_coins=1000, item_type="badge"),
]

@router.get("/items", response_model=List[StoreItem])
def get_store_items():
    return STORE_ITEMS

class PurchaseRequest(BaseModel):
    user_id: int
    item_id: int

@router.post("/purchase")
def purchase_item(request: PurchaseRequest):
    # In a real app, check if user has enough coins, deduct coins, and save to DB
    item = next((i for i in STORE_ITEMS if i.id == request.item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    return {"status": "success", "message": f"Successfully purchased {item.name}", "remaining_coins": 150} # Mock remaining coins
