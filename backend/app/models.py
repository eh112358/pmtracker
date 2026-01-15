from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Metal(Base):
    __tablename__ = "metals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    symbol = Column(String(10), unique=True, nullable=False)

    products = relationship("Product", back_populates="metal")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    metal_id = Column(Integer, ForeignKey("metals.id"), nullable=False)
    weight_oz = Column(Float, nullable=False)
    description = Column(Text, nullable=True)

    metal = relationship("Metal", back_populates="products")
    holdings = relationship("Holding", back_populates="product")


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    purchase_date = Column(Date, nullable=False)
    purchase_price_per_oz = Column(Float, nullable=False)
    premium_paid = Column(Float, nullable=True, default=0.0)
    dealer = Column(String(100), nullable=True)
    storage_location = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="holdings")
