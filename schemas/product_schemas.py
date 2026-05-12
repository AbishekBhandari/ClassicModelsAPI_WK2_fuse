from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    productName: str = Field(..., max_length=70)
    productLine: str = Field(..., max_length=50)
    productScale: str = Field(..., max_length=10)
    productVendor: str = Field(..., max_length=50)
    productDescription: str
    quantityInStock: int = Field(..., ge=0)
    buyPrice: Decimal = Field(..., ge=0)
    MSRP: Decimal = Field(..., ge=0)


class ProductCreate(ProductBase):
    productCode: str = Field(..., max_length=15)


class ProductUpdate(BaseModel):
    productName: Optional[str] = Field(None, max_length=70)
    productLine: Optional[str] = Field(None, max_length=50)
    productScale: Optional[str] = Field(None, max_length=10)
    productVendor: Optional[str] = Field(None, max_length=50)
    productDescription: Optional[str] = None
    quantityInStock: Optional[int] = Field(None, ge=0)
    buyPrice: Optional[Decimal] = Field(None, ge=0)
    MSRP: Optional[Decimal] = Field(None, ge=0)


class ProductOut(ProductCreate):
    class Config:
        from_attributes = True


class ProductOrderDetail(BaseModel):
    orderNumber: int
    productCode: str = Field(..., max_length=15)
    quantityOrdered: int = Field(..., ge=1)
    priceEach: Decimal = Field(..., ge=0)
    orderLineNumber: int = Field(..., ge=1)
