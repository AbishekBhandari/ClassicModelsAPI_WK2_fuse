from typing import Optional

from pydantic import BaseModel, Field


class OfficeCreate(BaseModel):
    officeCode: str = Field(..., max_length=10)
    city: str = Field(..., max_length=50)
    phone: str = Field(..., max_length=50)
    addressLine1: str = Field(..., max_length=50)
    addressLine2: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    country: str = Field(..., max_length=50)
    postalCode: str = Field(..., max_length=15)
    territory: str = Field(..., max_length=10)


class OfficeOut(BaseModel):
    officeCode: str
    city: str
    phone: str
    addressLine1: str
    addressLine2: Optional[str] = None
    state: Optional[str] = None
    country: str
    postalCode: str
    territory: str

    class Config:
        from_attributes = True


class OfficeUpdate(BaseModel):
    officeCode: Optional[str] = Field(None, max_length=10)
    city: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=50)
    addressLine1: Optional[str] = Field(None, max_length=50)
    addressLine2: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=50)
    postalCode: Optional[str] = Field(None, max_length=15)
    territory: Optional[str] = Field(None, max_length=10)
