from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PaymentBase(BaseModel):
    paymentDate: date
    amount: Decimal = Field(..., gt=0)

    @field_validator("paymentDate")
    @classmethod
    def validate_payment_date_not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("paymentDate cannot be in the future")
        return value


class PaymentCreate(PaymentBase):
    customerNumber: int
    checkNumber: str = Field(..., max_length=50)


class PaymentOut(BaseModel):
    customerNumber: int
    checkNumber: str
    paymentDate: date
    amount: Decimal

    class Config:
        from_attributes = True


class PaymentUpdate(BaseModel):
    customerNumber: Optional[int] = None
    checkNumber: Optional[str] = Field(None, max_length=50)
    paymentDate: Optional[date] = None
    amount: Optional[Decimal] = Field(None, gt=0)

    @field_validator("paymentDate")
    @classmethod
    def validate_payment_date_not_in_future(cls, value: Optional[date]) -> Optional[date]:
        if value is not None and value > date.today():
            raise ValueError("paymentDate cannot be in the future")
        return value
