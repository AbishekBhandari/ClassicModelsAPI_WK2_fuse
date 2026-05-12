from typing import Optional

from pydantic import BaseModel, Field


class ProductLineCreate(BaseModel):
    productLine: str = Field(..., max_length=50)
    textDescription: Optional[str] = Field(None, max_length=4000)
    htmlDescription: Optional[str] = None
    image: Optional[bytes] = None


class ProductLineOut(BaseModel):
    productLine: str
    textDescription: Optional[str] = None
    htmlDescription: Optional[str] = None

    class Config:
        from_attributes = True


class ProductLineUpdate(BaseModel):
    productLine: Optional[str] = Field(None, max_length=50)
    textDescription: Optional[str] = Field(None, max_length=4000)
    htmlDescription: Optional[str] = None
    image: Optional[bytes] = None
