from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    customerNumber: int
    customerName: str = Field(..., max_length=50)
    contactLastName: str = Field(..., max_length=50)
    contactFirstName: str = Field(..., max_length=50)
    phone: str = Field(..., max_length=50)
    addressLine1: str = Field(..., max_length=50)
    addressLine2: Optional[str] = Field(None, max_length=50)
    city: str = Field(..., max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    postalCode: Optional[str] = Field(None, max_length=15)
    country: str = Field(..., max_length=50)
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[Decimal] = Field(None, ge=0)


class CustomerOut(BaseModel):
    customerNumber: int
    customerName: str
    contactLastName: str
    contactFirstName: str
    phone: str
    addressLine1: str
    addressLine2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: str
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[Decimal] = None

    class Config:
        from_attributes = True


class CustomerUpdate(BaseModel):
    customerNumber: Optional[int] = None
    customerName: Optional[str] = Field(None, max_length=50)
    contactLastName: Optional[str] = Field(None, max_length=50)
    contactFirstName: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=50)
    addressLine1: Optional[str] = Field(None, max_length=50)
    addressLine2: Optional[str] = Field(None, max_length=50)
    city: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    postalCode: Optional[str] = Field(None, max_length=15)
    country: Optional[str] = Field(None, max_length=50)
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[Decimal] = Field(None, ge=0)
