from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from ..database import get_db
from ..auth import get_current_user
from .. import models, schemas

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/", response_model=List[schemas.Product])
def get_products(
    metal_id: int = None,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    query = db.query(models.Product).options(joinedload(models.Product.metal))
    if metal_id:
        query = query.filter(models.Product.metal_id == metal_id)
    return query.all()


@router.get("/{product_id}", response_model=schemas.Product)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    product = (
        db.query(models.Product)
        .options(joinedload(models.Product.metal))
        .filter(models.Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    # Verify metal exists
    metal = db.query(models.Metal).filter(models.Metal.id == product.metal_id).first()
    if not metal:
        raise HTTPException(status_code=400, detail="Metal not found")

    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    holdings_count = db.query(models.Holding).filter(models.Holding.product_id == product_id).count()
    if holdings_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete product: {holdings_count} holding(s) reference it. Delete those holdings first."
        )

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}
