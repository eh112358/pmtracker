from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional


# Metal schemas
class MetalBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    symbol: str = Field(..., min_length=1, max_length=10)

    @field_validator('name', 'symbol')
    @classmethod
    def not_empty_string(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Value cannot be empty or whitespace only')
        return v.strip()


class MetalCreate(MetalBase):
    pass


class Metal(MetalBase):
    id: int

    class Config:
        from_attributes = True


# Product schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    metal_id: int = Field(..., gt=0)
    weight_oz: float = Field(..., gt=0, le=10000, description="Weight must be positive and <= 10000 oz")
    description: Optional[str] = Field(None, max_length=500)

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Product name cannot be empty')
        return v.strip()

    @field_validator('description')
    @classmethod
    def clean_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            return v if v else None
        return v


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    metal: Optional[Metal] = None

    class Config:
        from_attributes = True


# Holding schemas
class HoldingBase(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(1, gt=0, le=100000, description="Quantity must be positive")
    purchase_date: date
    purchase_price_per_oz: float = Field(..., gt=0, le=1000000, description="Price must be positive")
    premium_paid: Optional[float] = Field(0.0, ge=0, le=100000)
    dealer: Optional[str] = Field(None, max_length=100)
    storage_location: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('purchase_date')
    @classmethod
    def date_not_in_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError('Purchase date cannot be in the future')
        return v

    @field_validator('dealer', 'storage_location')
    @classmethod
    def clean_optional_string(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            return v if v else None
        return v


class HoldingCreate(HoldingBase):
    pass


class HoldingUpdate(BaseModel):
    product_id: Optional[int] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, gt=0, le=100000)
    purchase_date: Optional[date] = None
    purchase_price_per_oz: Optional[float] = Field(None, gt=0, le=1000000)
    premium_paid: Optional[float] = Field(None, ge=0, le=100000)
    dealer: Optional[str] = Field(None, max_length=100)
    storage_location: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('purchase_date')
    @classmethod
    def date_not_in_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError('Purchase date cannot be in the future')
        return v


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
    updated_at: datetime
    is_fallback: Optional[bool] = False
