from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from crud.payment_crud import (
    create_payments,
    delete_payments,
    get_payment_by_primary_key,
    get_payments,
    get_payments_by_customer,
    update_payments,
    count_payments,
)
from database import get_db
from schemas.payment_schemas import PaymentCreate, PaymentOut, PaymentUpdate

router = APIRouter(tags=["payments"])


@router.get("/count")
def read_count(db: Session = Depends(get_db)):
    total = count_payments(db)
    return {"count": total}

@router.get("/", response_model=List[PaymentOut])
def read_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_payments(db, skip=skip, limit=limit)


@router.get("/customer/{customerNumber}", response_model=List[PaymentOut])
def read_payments_by_customer(
    customerNumber: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_payments_by_customer(db, customerNumber, skip=skip, limit=limit)


@router.get("/{customerNumber}/{checkNumber}", response_model=PaymentOut)
def read_payment(customerNumber: int, checkNumber: str, db: Session = Depends(get_db)):
    return get_payment_by_primary_key(db, customerNumber, checkNumber)


@router.post("/", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_new_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    return create_payments(db, payment)


@router.put("/{customerNumber}/{checkNumber}", response_model=PaymentOut)
def update_existing_payment(
    customerNumber: int,
    checkNumber: str,
    payment_update: PaymentUpdate,
    db: Session = Depends(get_db),
):
    return update_payments(db, customerNumber, checkNumber, payment_update)


@router.delete("/{customerNumber}/{checkNumber}", response_model=PaymentOut)
def remove_payment(customerNumber: int, checkNumber: str, db: Session = Depends(get_db)):
    return delete_payments(db, customerNumber, checkNumber)
