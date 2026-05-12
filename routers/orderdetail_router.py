from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from crud.orderdetail_crud import (
    create_orderdetails,
    delete_orderdetails,
    get_orderdetail,
    get_orderdetails,
    update_orderdetails,
    count_orderdetails,
)
from database import get_db
from schemas.orderdetail_schemas import (
    OrderDetailCreate,
    OrderDetailOut,
    OrderDetailUpdate,
)

router = APIRouter(tags=["orderdetails"])


@router.get("/count")
def read_count(db: Session = Depends(get_db)):
    total = count_orderdetails(db)
    return {"count": total}

@router.get("/", response_model=List[OrderDetailOut])
def read_orderdetails(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_orderdetails(db, skip=skip, limit=limit)


@router.get("/{orderNumber}/{productCode}", response_model=OrderDetailOut)
def read_orderdetail(
    orderNumber: int,
    productCode: str,
    db: Session = Depends(get_db),
):
    return get_orderdetail(db, orderNumber, productCode)


@router.post("/", response_model=OrderDetailOut, status_code=status.HTTP_201_CREATED)
def create_new_orderdetail(orderdetail: OrderDetailCreate, db: Session = Depends(get_db)):
    return create_orderdetails(db, orderdetail)


@router.put("/{orderNumber}/{productCode}", response_model=OrderDetailOut)
def update_existing_orderdetail(
    orderNumber: int,
    productCode: str,
    orderdetail_update: OrderDetailUpdate,
    db: Session = Depends(get_db),
):
    return update_orderdetails(db, orderNumber, productCode, orderdetail_update)


@router.delete("/{orderNumber}/{productCode}", response_model=OrderDetailOut)
def remove_orderdetail(
    orderNumber: int,
    productCode: str,
    db: Session = Depends(get_db),
):
    return delete_orderdetails(db, orderNumber, productCode)
