from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from crud.productline_crud import (
    create_productlines,
    delete_productlines,
    get_productline_by_primary_key,
    get_productlines,
    update_productlines,
    count_productlines,
)
from database import get_db
from schemas.productline_schemas import (
    ProductLineCreate,
    ProductLineOut,
    ProductLineUpdate,
)

router = APIRouter(tags=["productlines"])


@router.get("/count")
def read_count(db: Session = Depends(get_db)):
    total = count_productlines(db)
    return {"count": total}

@router.get("/", response_model=List[ProductLineOut])
def read_productlines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_productlines(db, skip=skip, limit=limit)


@router.get("/{productLine}", response_model=ProductLineOut)
def read_productline(productLine: str, db: Session = Depends(get_db)):
    return get_productline_by_primary_key(db, productLine)


@router.post("/", response_model=ProductLineOut, status_code=status.HTTP_201_CREATED)
def create_new_productline(productline: ProductLineCreate, db: Session = Depends(get_db)):
    return create_productlines(db, productline)


@router.put("/{productLine}", response_model=ProductLineOut)
def update_existing_productline(
    productLine: str,
    productline_update: ProductLineUpdate,
    db: Session = Depends(get_db),
):
    return update_productlines(db, productLine, productline_update)


@router.delete("/{productLine}", response_model=ProductLineOut)
def remove_productline(productLine: str, db: Session = Depends(get_db)):
    return delete_productlines(db, productLine)
