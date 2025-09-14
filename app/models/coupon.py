from pydantic import BaseModel,Field 
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from enum import Enum

class CouponType(str, Enum):
    CART_WISE = "cart-wise"
    PRODUCT_WISE = "product-wise"
    BXGY = "bxgy"

# Cart-wise coupon details
class CartWiseDetails(BaseModel):
    threshold: float
    discount: float  # percentage
    max_discount: Optional[float] = None

# Product-wise coupon details
class ProductWiseDetails(BaseModel):
    product_id: int
    discount: float  # percentage
    max_discount: Optional[float] = None

# BxGy coupon details
class BuyProduct(BaseModel):
    product_id: int
    quantity: int

class GetProduct(BaseModel):
    product_id: int
    quantity: int

class BxGyDetails(BaseModel):
    buy_products: List[BuyProduct]
    get_products: List[GetProduct]
    repition_limit: int

class CouponCreate(BaseModel):
    type: CouponType
    details: Union[CartWiseDetails, ProductWiseDetails, BxGyDetails]
    expires_at: Optional[datetime] = None
    usage_limit: Optional[int] = None

class CouponResponse(BaseModel):
    id: int
    type: str
    details: Dict[str, Any]
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None

class ApplicableCoupon(BaseModel):
    coupon_id: int
    type: str
    discount: float
    
    class Config:
        from_attributes = True  
        orm_mode = True        
        arbitrary_types_allowed = True