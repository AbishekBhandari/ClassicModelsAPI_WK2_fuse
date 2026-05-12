from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class OrderDetailCreate(BaseModel):
    orderNumber: int
    productCode: str = Field(..., max_length=15)
    quantityOrdered: int = Field(..., gt=0)
    priceEach: Decimal = Field(..., ge=0)
    orderLineNumber: int = Field(..., ge=1, le=32767)


class OrderDetailOut(BaseModel):
    orderNumber: int
    productCode: str
    quantityOrdered: int
    priceEach: Decimal
    orderLineNumber: int

    class Config:
        from_attributes = True


class OrderDetailUpdate(BaseModel):
    orderNumber: Optional[int] = None
    productCode: Optional[str] = Field(None, max_length=15)
    quantityOrdered: Optional[int] = Field(None, gt=0)
    priceEach: Optional[Decimal] = Field(None, ge=0)
    orderLineNumber: Optional[int] = Field(None, ge=1, le=32767)
