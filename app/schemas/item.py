"""Pydantic schemas for inventory operations."""
from pydantic import BaseModel, ConfigDict, Field

class ItemCreate(BaseModel):
    """Payload used to create an inventory item."""
    sku: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    quantity: int = Field(ge=0)
    unit_price: float = Field(gt=0)

class ItemOut(ItemCreate):
    """Inventory item returned by the API."""
    id: int
    model_config = ConfigDict(from_attributes=True)

class MovementRequest(BaseModel):
    """Payload used to move stock in or out."""
    quantity: int = Field(gt=0)
    reason: str = Field(min_length=3, max_length=200)
