from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from crud.order_crud import (
    create_orders,
    delete_orders,
    get_order_by_primary_key,
    get_orders,
    get_orders_by_customer,
    update_orders,
    count_orders,
)
from database import get_db
from schemas.order_schemas import OrderCreate, OrderOut, OrderUpdate

router = APIRouter(tags=["orders"])


@router.get("/count")
def read_count(db: Session = Depends(get_db)):
    total = count_orders(db)
    return {"count": total}

@router.get("/", response_model=List[OrderOut])
def read_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_orders(db, skip=skip, limit=limit)


@router.get("/customer/{customerNumber}", response_model=List[OrderOut])
def read_orders_by_customer(
    customerNumber: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_orders_by_customer(db, customerNumber, skip=skip, limit=limit)


@router.get("/{orderNumber}", response_model=OrderOut)
def read_order(orderNumber: int, db: Session = Depends(get_db)):
    return get_order_by_primary_key(db, orderNumber)


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_new_order(order: OrderCreate, db: Session = Depends(get_db)):
    return create_orders(db, order)


@router.put("/{orderNumber}", response_model=OrderOut)
def update_existing_order(
    orderNumber: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
):
    return update_orders(db, orderNumber, order_update)


@router.delete("/{orderNumber}", response_model=OrderOut)
def remove_order(orderNumber: int, db: Session = Depends(get_db)):
    return delete_orders(db, orderNumber)
