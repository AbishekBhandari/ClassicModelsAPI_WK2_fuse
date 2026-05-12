from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crud.product_crud import (
    create_product,
    delete_product,
    get_product_by_code,
    get_product_orderdetails,
    get_products,
    update_product,
    count_products,
)
from database import get_db
from schemas.product_schemas import (
    ProductCreate,
    ProductOrderDetail,
    ProductOut,
    ProductUpdate,
)

router = APIRouter(tags=["products"])


@router.get("/count")
def read_count(db: Session = Depends(get_db)):
    total = count_products(db)
    return {"count": total}

@router.get("/", response_model=List[ProductOut])
def read_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_products(db, skip=skip, limit=limit)


@router.get("/{productCode}", response_model=ProductOut)
def read_product(productCode: str, db: Session = Depends(get_db)):
    product = get_product_by_code(db, productCode)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_new_product(product: ProductCreate, db: Session = Depends(get_db)):
    existing = get_product_by_code(db, product.productCode)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with this code already exists",
        )
    try:
        return create_product(db, product)
    except IntegrityError as exc:
        db.rollback()
        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()
        if "productline" in error_text and "foreign key" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Invalid productLine '{product.productLine}'. "
                    "It must reference an existing productlines.productLine."
                ),
            ) from exc
        raise


@router.put("/{productCode}", response_model=ProductOut)
def update_existing_product(
    productCode: str, product_update: ProductUpdate, db: Session = Depends(get_db)
):
    product = update_product(db, productCode, product_update)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.delete("/{productCode}", response_model=ProductOut)
def remove_product(productCode: str, db: Session = Depends(get_db)):
    deleted = delete_product(db, productCode)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return deleted


@router.get("/{productCode}/orderdetails", response_model=List[ProductOrderDetail])
def read_product_orderdetails(productCode: str, db: Session = Depends(get_db)):
    product = get_product_by_code(db, productCode)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return get_product_orderdetails(db, productCode)



