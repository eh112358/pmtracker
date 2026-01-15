from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List

from ..database import get_db
from .. import models, schemas
from ..services.price_service import price_service

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("/prices", response_model=schemas.SpotPrices)
async def get_spot_prices():
    """Get current spot prices for all metals."""
    prices = await price_service.get_spot_prices()
    return schemas.SpotPrices(**prices)


@router.get("/holdings", response_model=List[schemas.HoldingWithValue])
async def get_holdings_with_values(db: Session = Depends(get_db)):
    """Get all holdings with current values and profit/loss calculations."""
    holdings = (
        db.query(models.Holding)
        .options(
            joinedload(models.Holding.product).joinedload(models.Product.metal)
        )
        .all()
    )

    prices = await price_service.get_spot_prices()

    result = []
    for holding in holdings:
        metal_symbol = holding.product.metal.symbol.lower()
        current_spot = prices.get(metal_symbol, 0)

        total_weight = holding.product.weight_oz * holding.quantity
        total_cost = (holding.purchase_price_per_oz * total_weight) + (holding.premium_paid or 0)
        current_value = current_spot * total_weight
        profit_loss = current_value - total_cost
        profit_loss_percent = (profit_loss / total_cost * 100) if total_cost > 0 else 0

        holding_dict = {
            "id": holding.id,
            "product_id": holding.product_id,
            "quantity": holding.quantity,
            "purchase_date": holding.purchase_date,
            "purchase_price_per_oz": holding.purchase_price_per_oz,
            "premium_paid": holding.premium_paid,
            "dealer": holding.dealer,
            "storage_location": holding.storage_location,
            "notes": holding.notes,
            "created_at": holding.created_at,
            "updated_at": holding.updated_at,
            "product": holding.product,
            "current_spot_price": current_spot,
            "total_weight_oz": total_weight,
            "total_cost": total_cost,
            "current_value": current_value,
            "profit_loss": profit_loss,
            "profit_loss_percent": profit_loss_percent,
        }
        result.append(schemas.HoldingWithValue(**holding_dict))

    return result


@router.get("/summary", response_model=schemas.PortfolioSummary)
async def get_portfolio_summary(db: Session = Depends(get_db)):
    """Get overall portfolio summary with totals and allocation."""
    holdings = (
        db.query(models.Holding)
        .options(
            joinedload(models.Holding.product).joinedload(models.Product.metal)
        )
        .all()
    )

    if not holdings:
        return schemas.PortfolioSummary(
            total_cost=0,
            current_value=0,
            total_profit_loss=0,
            total_profit_loss_percent=0,
            holdings_count=0,
            allocation_by_metal={}
        )

    prices = await price_service.get_spot_prices()

    total_cost = 0
    current_value = 0
    allocation_by_metal = {}

    for holding in holdings:
        metal_name = holding.product.metal.name
        metal_symbol = holding.product.metal.symbol.lower()
        current_spot = prices.get(metal_symbol, 0)

        total_weight = holding.product.weight_oz * holding.quantity
        cost = (holding.purchase_price_per_oz * total_weight) + (holding.premium_paid or 0)
        value = current_spot * total_weight

        total_cost += cost
        current_value += value

        if metal_name not in allocation_by_metal:
            allocation_by_metal[metal_name] = 0
        allocation_by_metal[metal_name] += value

    # Convert allocation to percentages
    if current_value > 0:
        allocation_by_metal = {
            metal: round((value / current_value) * 100, 2)
            for metal, value in allocation_by_metal.items()
        }

    total_profit_loss = current_value - total_cost
    total_profit_loss_percent = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0

    return schemas.PortfolioSummary(
        total_cost=round(total_cost, 2),
        current_value=round(current_value, 2),
        total_profit_loss=round(total_profit_loss, 2),
        total_profit_loss_percent=round(total_profit_loss_percent, 2),
        holdings_count=len(holdings),
        allocation_by_metal=allocation_by_metal
    )
