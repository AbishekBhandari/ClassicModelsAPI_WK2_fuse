from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from crud.customer_crud import (
    create_customers,
    delete_customers,
    get_customer_by_primary_key,
    get_customers,
    update_customers,
    count_customers,
)
from database import get_db
from schemas.customer_schemas import CustomerCreate, CustomerOut, CustomerUpdate

router = APIRouter(tags=["customers"])


@router.get("/count")
def read_count(db: Session = Depends(get_db)):
    total = count_customers(db)
    return {"count": total}

@router.get("/", response_model=List[CustomerOut])
def read_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_customers(db, skip=skip, limit=limit)


@router.get("/{customerNumber}", response_model=CustomerOut)
def read_customer(customerNumber: int, db: Session = Depends(get_db)):
    return get_customer_by_primary_key(db, customerNumber)


@router.post("/", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_new_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    return create_customers(db, customer)


@router.put("/{customerNumber}", response_model=CustomerOut)
def update_existing_customer(
    customerNumber: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
):
    return update_customers(db, customerNumber, customer_update)


@router.delete("/{customerNumber}", response_model=CustomerOut)
def remove_customer(customerNumber: int, db: Session = Depends(get_db)):
    return delete_customers(db, customerNumber)
