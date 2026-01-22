from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field


class CreateBookingRequest(BaseModel):
    car_id: int = Field(..., ge=1, description="ID of the car to book")
    start_date: date = Field(..., description="Booking start date")
    end_date: date = Field(..., description="Booking end date")
    customer_name: str = Field(..., min_length=1, description="Name of the customer")

class BookingResponse(BaseModel):
    id: int = Field(...)
    car_id: int = Field(...)
    start_date: date = Field(...)
    end_date: date = Field(...)
    customer_name: str = Field(...)
