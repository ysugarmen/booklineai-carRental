from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field


class CreateBookingRequest(BaseModel):
    car_id: int = Field(..., min_length=1)
    start_date: date = Field(...)
    end_date: date = Field(...)
    customer_name: str = Field(..., min_length=1)

class BookingResponse(BaseModel):
    id: int = Field(...)
    car_id: int = Field(...)
    start_date: date = Field(...)
    end_date: date = Field(...)
    customer_name: str = Field(...)
