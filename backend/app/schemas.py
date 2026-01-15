from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


# Metal schemas
class MetalBase(BaseModel):
    name: str
    symbol: str


class MetalCreate(MetalBase):
    pass


class Metal(MetalBase):
    id: int

    class Config:
        from_attributes = True


# Product schemas
class ProductBase(BaseModel):
    name: str
    metal_id: int
    weight_oz: float
    description: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    metal: Optional[Metal] = None

    class Config:
        from_attributes = True


# Holding schemas
class HoldingBase(BaseModel):
    product_id: int
    quantity: int = 1
    purchase_date: date
    purchase_price_per_oz: float
    premium_paid: Optional[float] = 0.0
    dealer: Optional[str] = None
    storage_location: Optional[str] = None
    notes: Optional[str] = None


class HoldingCreate(HoldingBase):
    pass


class HoldingUpdate(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    purchase_date: Optional[date] = None
    purchase_price_per_oz: Optional[float] = None
    premium_paid: Optional[float] = None
    dealer: Optional[str] = None
    storage_location: Optional[str] = None
    notes: Optional[str] = None


class Holding(HoldingBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    product: Optional[Product] = None

    class Config:
        from_attributes = True


# Portfolio summary schemas
class HoldingWithValue(Holding):
    current_spot_price: float
    total_weight_oz: float
    total_cost: float
    current_value: float
    profit_loss: float
    profit_loss_percent: float


class PortfolioSummary(BaseModel):
    total_cost: float
    current_value: float
    total_profit_loss: float
    total_profit_loss_percent: float
    holdings_count: int
    allocation_by_metal: dict[str, float]


class SpotPrices(BaseModel):
    gold: float
    silver: float
    platinum: float
    palladium: float
    updated_at: datetime
