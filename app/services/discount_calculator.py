from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models.database import CouponDB
from ..models.cart import Cart, CartItem, UpdatedCartResponse
from ..models.coupon import ApplicableCoupon
from typing import List, Optional
from datetime import datetime

class DiscountCalculator:
    def __init__(self, db: Session):
        self.db = db

   
    def get_applicable_coupons(self, cart: Cart) -> List[ApplicableCoupon]:
        applicable = []
        
        # Make sure to properly query and load the objects
        coupons = self.db.query(CouponDB).filter(
            CouponDB.is_active == True
        ).all()
        
        import json
        for coupon in coupons:
            self.db.refresh(coupon)
            details = coupon.details
            if isinstance(details, str):
                details = json.loads(details)
            if self._is_coupon_valid(coupon):
                discount = self._calculate_discount(coupon, cart, details)
                if discount > 0:
                    applicable_coupon = ApplicableCoupon(
                        coupon_id=int(coupon.id),
                        type=str(coupon.type),
                        discount=float(discount)
                    )
                    applicable.append(applicable_coupon)
        
        return applicable

    def apply_coupon(self, coupon_id: int, cart: Cart) -> Optional[UpdatedCartResponse]:
        coupon = self.db.query(CouponDB).filter(
            CouponDB.id == coupon_id,
            CouponDB.is_active == True
        ).first()
        
        if not coupon or not self._is_coupon_valid(coupon):
            return None

        import json
        details = coupon.details
        if isinstance(details, str):
            details = json.loads(details)
        return self._apply_coupon_to_cart(coupon, cart, details)

    def _is_coupon_valid(self, coupon: CouponDB) -> bool:
        # Check expiration
        if coupon.expires_at and coupon.expires_at < datetime.utcnow():
            return False
        
        # Check usage limit
        if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
            return False
            
        return True

    def _calculate_discount(self, coupon: CouponDB, cart: Cart, details: dict) -> float:
        if coupon.type == "cart-wise":
            return self._calculate_cart_wise_discount(details, cart)
        elif coupon.type == "product-wise":
            return self._calculate_product_wise_discount(details, cart)
        elif coupon.type == "bxgy":
            return self._calculate_bxgy_discount(details, cart)
        return 0

    def _calculate_cart_wise_discount(self, details: dict, cart: Cart) -> float:
        total = sum(item.quantity * item.price for item in cart.items)
        if total >= details["threshold"]:
            discount = total * (details["discount"] / 100)
            if "max_discount" in details and details["max_discount"]:
                discount = min(discount, details["max_discount"])
            return discount
        return 0

    def _calculate_product_wise_discount(self, details: dict, cart: Cart) -> float:
        target_product_id = details["product_id"]
        for item in cart.items:
            if item.product_id == target_product_id:
                discount = item.quantity * item.price * (details["discount"] / 100)
                if "max_discount" in details and details["max_discount"]:
                        discount = min(discount, details["max_discount"])
                return discount
        return 0

    def _calculate_bxgy_discount(self, details: dict, cart: Cart) -> float:
        # Create product inventory from cart
        cart_products = {item.product_id: item.quantity for item in cart.items}
        
        # Check how many times we can apply the offer
        max_applications = details.get("repetition_limit", 1)
        
        # Calculate how many buy products we have
        buy_satisfaction = float('inf')
        for buy_product in details["buy_products"]:
            available = cart_products.get(buy_product["product_id"], 0)
            required = buy_product["quantity"]
            buy_satisfaction = min(buy_satisfaction, available // required)
        
        if buy_satisfaction == 0:
            return 0
        
        # Limit by repetition limit
        actual_applications = min(buy_satisfaction, max_applications)
        
        # Calculate discount based on get products
        total_discount = 0
        for get_product in details["get_products"]:
            product_id = get_product["product_id"]
            free_quantity = get_product["quantity"] * actual_applications
            
            # Find the product in cart to get its price
            for item in cart.items:
                if item.product_id == product_id:
                    available_to_make_free = min(free_quantity, item.quantity)
                    total_discount += available_to_make_free * item.price
                    break
        
        return total_discount

    def _apply_coupon_to_cart(self, coupon: CouponDB, cart: Cart, details: dict) -> UpdatedCartResponse:
        # Create a copy of cart items
        updated_items = [
            CartItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                total_discount=0.0
            ) for item in cart.items
        ]
        
        total_discount = 0
        if coupon.type == "cart-wise":
            discount = self._calculate_cart_wise_discount(coupon.details, cart)
            target_product_id = details.get("product_id")
            for item in updated_items:
                if item.product_id == target_product_id:
                    item_discount = item.quantity * item.price * (details.get("discount", 0) / 100)
                    if "max_discount" in details and details["max_discount"]:
                        item_discount = min(item_discount, details["max_discount"])
                    item.total_discount = item_discount
                    total_discount = float(total_discount) + float(item_discount)
            cart_products = {item.product_id: item.quantity for item in cart.items}
            max_applications = details.get("repetition_limit", 1)
            buy_satisfaction = float('inf')
            for buy_product in details.get("buy_products", []):
                available = cart_products.get(buy_product["product_id"], 0)
                required = buy_product["quantity"]
                buy_satisfaction = min(buy_satisfaction, available // required)
            if buy_satisfaction > 0:
                actual_applications = min(buy_satisfaction, max_applications)
                for get_product in details.get("get_products", []):
                    product_id = get_product["product_id"]
                    free_quantity = get_product["quantity"] * actual_applications
                    for item in updated_items:
                        if item.product_id == product_id:
                            available_to_make_free = min(free_quantity, item.quantity)
                            item_discount = available_to_make_free * item.price
                            if item.total_discount is None:
                                item.total_discount = 0.0
                            item.total_discount = float(item.total_discount) + float(item_discount)
                            total_discount = float(total_discount) + float(item_discount)
                            break
                    product_id = get_product["product_id"]
                    free_quantity = get_product["quantity"] * actual_applications
                    
                    for item in updated_items:
                        if item.product_id == product_id:
                            available_to_make_free = min(free_quantity, item.quantity)
                            item_discount = available_to_make_free * item.price
                            item.total_discount = float(item.total_discount or 0.0) + float(item_discount)
                            total_discount += item_discount
                            break
        
        # Calculate totals
        total_price = sum(item.quantity * item.price for item in updated_items)
        final_price = total_price - total_discount
        
        # Update usage count
        coupon.used_count += 1
        self.db.commit()
        
        return UpdatedCartResponse(
            items=updated_items,
            total_price=total_price,
            total_discount=total_discount,
            final_price=final_price
        )