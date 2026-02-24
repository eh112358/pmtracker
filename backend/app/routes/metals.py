from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from ..database import get_db
from ..auth import get_current_user
from .. import models, schemas

router = APIRouter(prefix="/api/metals", tags=["metals"])


@router.get("/", response_model=List[schemas.Metal])
def get_metals(
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    return db.query(models.Metal).all()


@router.get("/{metal_id}", response_model=schemas.Metal)
def get_metal(
    metal_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    metal = db.query(models.Metal).filter(models.Metal.id == metal_id).first()
    if not metal:
        raise HTTPException(status_code=404, detail="Metal not found")
    return metal


@router.post("/", response_model=schemas.Metal, status_code=201)
def create_metal(
    metal: schemas.MetalCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(get_current_user)
):
    db_metal = models.Metal(**metal.model_dump())
    db.add(db_metal)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A metal with that name or symbol already exists."
        )
    db.refresh(db_metal)
    return db_metal
