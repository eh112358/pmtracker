from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/holdings", tags=["holdings"])


@router.get("/", response_model=List[schemas.Holding])
def get_holdings(db: Session = Depends(get_db)):
    return (
        db.query(models.Holding)
        .options(
            joinedload(models.Holding.product).joinedload(models.Product.metal)
        )
        .all()
    )


@router.get("/{holding_id}", response_model=schemas.Holding)
def get_holding(holding_id: int, db: Session = Depends(get_db)):
    holding = (
        db.query(models.Holding)
        .options(
            joinedload(models.Holding.product).joinedload(models.Product.metal)
        )
        .filter(models.Holding.id == holding_id)
        .first()
    )
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    return holding


@router.post("/", response_model=schemas.Holding)
def create_holding(holding: schemas.HoldingCreate, db: Session = Depends(get_db)):
    # Verify product exists
    product = db.query(models.Product).filter(models.Product.id == holding.product_id).first()
    if not product:
        raise HTTPException(status_code=400, detail="Product not found")

    db_holding = models.Holding(**holding.model_dump())
    db.add(db_holding)
    db.commit()
    db.refresh(db_holding)

    # Reload with relationships
    return (
        db.query(models.Holding)
        .options(
            joinedload(models.Holding.product).joinedload(models.Product.metal)
        )
        .filter(models.Holding.id == db_holding.id)
        .first()
    )


@router.put("/{holding_id}", response_model=schemas.Holding)
def update_holding(
    holding_id: int,
    holding_update: schemas.HoldingUpdate,
    db: Session = Depends(get_db)
):
    holding = db.query(models.Holding).filter(models.Holding.id == holding_id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    update_data = holding_update.model_dump(exclude_unset=True)

    # Verify product exists if being updated
    if "product_id" in update_data:
        product = db.query(models.Product).filter(
            models.Product.id == update_data["product_id"]
        ).first()
        if not product:
            raise HTTPException(status_code=400, detail="Product not found")

    for field, value in update_data.items():
        setattr(holding, field, value)

    db.commit()
    db.refresh(holding)

    # Reload with relationships
    return (
        db.query(models.Holding)
        .options(
            joinedload(models.Holding.product).joinedload(models.Product.metal)
        )
        .filter(models.Holding.id == holding.id)
        .first()
    )


@router.delete("/{holding_id}")
def delete_holding(holding_id: int, db: Session = Depends(get_db)):
    holding = db.query(models.Holding).filter(models.Holding.id == holding_id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    db.delete(holding)
    db.commit()
    return {"message": "Holding deleted"}
