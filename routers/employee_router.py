from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from crud.employee_crud import (
    create_employees,
    delete_employees,
    get_employee_by_primary_key,
    get_employee_reports,
    get_employees,
    update_employees,
    count_employees,
)
from database import get_db
from schemas.employee_schemas import EmployeeCreate, EmployeeOut, EmployeeUpdate

router = APIRouter(tags=["employees"])


@router.get("/count")
def read_count(db: Session = Depends(get_db)):
    total = count_employees(db)
    return {"count": total}

@router.get("/", response_model=List[EmployeeOut])
def read_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_employees(db, skip=skip, limit=limit)


@router.get("/{employeeNumber}", response_model=EmployeeOut)
def read_employee(employeeNumber: int, db: Session = Depends(get_db)):
    return get_employee_by_primary_key(db, employeeNumber)


@router.get("/{employeeNumber}/reports", response_model=List[EmployeeOut])
def read_employee_reports(
    employeeNumber: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_employee_reports(db, employeeNumber, skip=skip, limit=limit)


@router.post("/", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_new_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    return create_employees(db, employee)


@router.put("/{employeeNumber}", response_model=EmployeeOut)
def update_existing_employee(
    employeeNumber: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    return update_employees(db, employeeNumber, employee_update)


@router.delete("/{employeeNumber}", response_model=EmployeeOut)
def remove_employee(employeeNumber: int, db: Session = Depends(get_db)):
    return delete_employees(db, employeeNumber)
