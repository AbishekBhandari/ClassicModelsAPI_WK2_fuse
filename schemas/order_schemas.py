from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, model_validator


class OrderStatus(str, Enum):
    SHIPPED = "Shipped"
    RESOLVED = "Resolved"
    CANCELLED = "Cancelled"
    ON_HOLD = "On Hold"
    DISPUTED = "Disputed"
    IN_PROCESS = "In Process"


class OrderBase(BaseModel):
    orderDate: date
    requiredDate: date
    shippedDate: Optional[date] = None
    status: OrderStatus
    comments: Optional[str] = None
    customerNumber: int

    @model_validator(mode="after")
    def validate_dates(self):
        if self.requiredDate <= self.orderDate:
            raise ValueError("requiredDate must be after orderDate")
        if self.shippedDate is not None and self.status != OrderStatus.SHIPPED:
            raise ValueError("shippedDate can only be set when status is 'Shipped'")
        return self


class OrderCreate(OrderBase):
    orderNumber: int


class OrderOut(BaseModel):
    orderNumber: int
    orderDate: date
    requiredDate: date
    shippedDate: Optional[date] = None
    status: OrderStatus
    comments: Optional[str] = None
    customerNumber: int

    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    orderNumber: Optional[int] = None
    orderDate: Optional[date] = None
    requiredDate: Optional[date] = None
    shippedDate: Optional[date] = None
    status: Optional[OrderStatus] = None
    comments: Optional[str] = None
    customerNumber: Optional[int] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.requiredDate is not None and self.orderDate is not None:
            if self.requiredDate <= self.orderDate:
                raise ValueError("requiredDate must be after orderDate")
        if self.shippedDate is not None and self.status is not None and self.status != OrderStatus.SHIPPED:
            raise ValueError("shippedDate can only be set when status is 'Shipped'")
        return self
