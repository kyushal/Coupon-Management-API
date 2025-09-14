from fastapi import FastAPI
from app.routers import coupons
from app.models.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Coupon Management API",
    description="RESTful API for managing e-commerce discount coupons",
    version="1.0.0"
)

app.include_router(coupons.router, prefix="/api/v1", tags=["coupons"])

@app.get("/")
async def root():
    return {"message": "Coupon Management API is running!"}