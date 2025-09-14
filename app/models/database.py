from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Use absolute path for SQLite
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "coupons.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL debugging
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CouponDB(Base):
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String(50), index=True, nullable=False)
    details = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    usage_limit = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<CouponDB(id={self.id}, type='{self.type}')>"

def create_tables():
    Base.metadata.create_all(bind=engine)