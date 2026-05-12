from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from crud.office_crud import (
    create_offices,
    delete_offices,
    get_office_by_primary_key,
    get_office_employees,
    get_offices,
    update_offices,
    count_offices,
)
from database import get_db
from schemas.office_schemas import OfficeCreate, OfficeOut, OfficeUpdate

router = APIRouter(tags=["offices"])


@router.get("/count")
def read_count(db: Session = Depends(get_db)):
    total = count_offices(db)
    return {"count": total}

@router.get("/", response_model=List[OfficeOut])
def read_offices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_offices(db, skip=skip, limit=limit)


@router.get("/{officeCode}", response_model=OfficeOut)
def read_office(officeCode: str, db: Session = Depends(get_db)):
    return get_office_by_primary_key(db, officeCode)


@router.get("/{officeCode}/employees", response_model=List[Dict[str, Any]])
def read_office_employees(
    officeCode: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_office_employees(db, officeCode, skip=skip, limit=limit)


@router.post("/", response_model=OfficeOut, status_code=status.HTTP_201_CREATED)
def create_new_office(office: OfficeCreate, db: Session = Depends(get_db)):
    return create_offices(db, office)


@router.put("/{officeCode}", response_model=OfficeOut)
def update_existing_office(
    officeCode: str,
    office_update: OfficeUpdate,
    db: Session = Depends(get_db),
):
    return update_offices(db, officeCode, office_update)


@router.delete("/{officeCode}", response_model=OfficeOut)
def remove_office(officeCode: str, db: Session = Depends(get_db)):
    return delete_offices(db, officeCode)
