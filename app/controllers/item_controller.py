"""Inventory use cases."""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate

def list_items(db: Session) -> list[Item]:
    """List inventory items ordered by SKU."""
    return list(db.scalars(select(Item).order_by(Item.sku)).all())

def create_item(db: Session, payload: ItemCreate) -> Item:
    """Create a new SKU."""
    if db.scalar(select(Item).where(Item.sku == payload.sku)):
        raise HTTPException(status_code=409, detail="SKU already exists")
    item = Item(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def remove_stock(db: Session, item_id: int, quantity: int) -> Item:
    """Remove available units from an item."""
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.quantity < quantity:
        raise HTTPException(status_code=409, detail="Insufficient stock")
    item.quantity -= quantity
    db.commit()
    db.refresh(item)
    return item

def reserve_stock(db: Session, item_id: int, quantity: int) -> Item:
    """Reserve available units without changing physical stock."""
    item = db.get(Item, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    available_quantity = item.quantity - item.reserved_quantity

    if quantity > available_quantity:
        raise HTTPException(
            status_code=409,
            detail="Insufficient available stock",
        )

    item.reserved_quantity += quantity

    db.commit()
    db.refresh(item)

    return item
