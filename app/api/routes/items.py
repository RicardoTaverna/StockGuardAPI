"""Inventory routes."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.controllers import item_controller
from app.core.security import current_user
from app.db.database import get_db
from app.schemas.item import ItemCreate, ItemOut, MovementRequest
router = APIRouter(prefix="/items", tags=["Inventory"], dependencies=[Depends(current_user)])

@router.get("", response_model=list[ItemOut])
def get_items(db: Session = Depends(get_db)):
    """Return all inventory items."""
    return item_controller.list_items(db)

@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def post_item(payload: ItemCreate, db: Session = Depends(get_db)):
    """Create a new inventory item."""
    return item_controller.create_item(db, payload)

@router.post("/{item_id}/withdraw", response_model=ItemOut)
def withdraw(item_id: int, payload: MovementRequest, db: Session = Depends(get_db)):
    """Withdraw units from an inventory item."""
    return item_controller.remove_stock(db, item_id, payload.quantity)

@router.patch("/{item_id}/deactivate", response_model=ItemOut)
def deactivate(item_id: int, db: Session = Depends(get_db)):
    """Deactivate an inventory item."""
    return item_controller.deactivate_item(db, item_id)
