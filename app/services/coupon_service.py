from sqlalchemy.orm import Session
from ..models.coupon import CouponCreate, CouponResponse
from ..models.database import CouponDB
from typing import List, Optional
import json

class CouponService:
    def __init__(self, db: Session):
        self.db = db

    def create_coupon(self, coupon: CouponCreate) -> CouponResponse:
        db_coupon = CouponDB(
            type=coupon.type,
            details=coupon.details.dict(),
            expires_at=coupon.expires_at,
            usage_limit=coupon.usage_limit
        )
        self.db.add(db_coupon)
        self.db.commit()
        self.db.refresh(db_coupon)
        return self._to_response(db_coupon)

    def get_all_coupons(self) -> List[CouponResponse]:
        coupons = self.db.query(CouponDB).filter(CouponDB.is_active == True).all()
        return [self._to_response(coupon) for coupon in coupons]

    def get_coupon_by_id(self, coupon_id: int) -> Optional[CouponResponse]:
        coupon = self.db.query(CouponDB).filter(
            CouponDB.id == coupon_id, 
            CouponDB.is_active == True
        ).first()
        return self._to_response(coupon) if coupon else None

    def update_coupon(self, coupon_id: int, coupon: CouponCreate) -> Optional[CouponResponse]:
        db_coupon = self.db.query(CouponDB).filter(CouponDB.id == coupon_id).first()
        if not db_coupon:
            return None
        
        db_coupon.type = coupon.type
        db_coupon.details = coupon.details.dict()
        db_coupon.expires_at = coupon.expires_at
        db_coupon.usage_limit = coupon.usage_limit
        
        self.db.commit()
        self.db.refresh(db_coupon)
        return self._to_response(db_coupon)

    def delete_coupon(self, coupon_id: int) -> bool:
        coupon = self.db.query(CouponDB).filter(CouponDB.id == coupon_id).first()
        if not coupon:
            return False
        coupon.is_active = False
        self.db.commit()
        return True

    def _to_response(self, coupon: CouponDB) -> CouponResponse:
        return CouponResponse(
            id=coupon.id,
            type=coupon.type,
            details=coupon.details,
            is_active=coupon.is_active,
            created_at=coupon.created_at,
            expires_at=coupon.expires_at
        )