from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.database import SessionLocal, CouponDB
from app.models.coupon import CouponCreate, CouponResponse, ApplicableCoupon
from app.models.cart import Cart, UpdatedCartResponse
from app.services.coupon_service import CouponService
from app.services.discount_calculator import DiscountCalculator

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/coupons", response_model=CouponResponse)
async def create_coupon(coupon: CouponCreate, db: Session = Depends(get_db)):
    service = CouponService(db)
    return service.create_coupon(coupon)

@router.get("/coupons", response_model=List[CouponResponse])
async def get_coupons(db: Session = Depends(get_db)):
    service = CouponService(db)
    return service.get_all_coupons()

@router.get("/coupons/{coupon_id}", response_model=CouponResponse)
async def get_coupon(coupon_id: int, db: Session = Depends(get_db)):
    service = CouponService(db)
    coupon = service.get_coupon_by_id(coupon_id)
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return coupon

@router.put("/coupons/{coupon_id}", response_model=CouponResponse)
async def update_coupon(coupon_id: int, coupon: CouponCreate, db: Session = Depends(get_db)):
    service = CouponService(db)
    updated = service.update_coupon(coupon_id, coupon)
    if not updated:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return updated

@router.delete("/coupons/{coupon_id}")
async def delete_coupon(coupon_id: int, db: Session = Depends(get_db)):
    service = CouponService(db)
    if not service.delete_coupon(coupon_id):
        raise HTTPException(status_code=404, detail="Coupon not found")
    return {"message": "Coupon deleted successfully"}

@router.post("/applicable-coupons")
async def get_applicable_coupons(request: dict, db: Session = Depends(get_db)):
    cart = Cart(**request["cart"])
    calculator = DiscountCalculator(db)
    return {"applicable_coupons": calculator.get_applicable_coupons(cart)}

@router.post("/apply-coupon/{coupon_id}")
async def apply_coupon(coupon_id: int, request: dict, db: Session = Depends(get_db)):
    cart = Cart(**request["cart"])
    calculator = DiscountCalculator(db)
    updated_cart = calculator.apply_coupon(coupon_id, cart)
    if not updated_cart:
        raise HTTPException(status_code=400, detail="Coupon cannot be applied")
    return {"updated_cart": updated_cart}