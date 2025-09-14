from pydantic import BaseModel
from typing import List, Optional

class CartItem(BaseModel):
    product_id: int
    quantity: int
    price: float
    total_discount: Optional[float] = 0

class Cart(BaseModel):
    items: List[CartItem]

class UpdatedCartResponse(BaseModel):
    items: List[CartItem]
    total_price: float
    total_discount: float
    final_price: float