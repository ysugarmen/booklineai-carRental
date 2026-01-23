from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field, model_validator
from typing import Self


class CreateBookingRequest(BaseModel):
    car_id: int = Field(..., ge=1, description="ID of the car to book")
    start_date: date = Field(..., description="Booking start date")
    end_date: date = Field(..., description="Booking end date")
    customer_name: str = Field(..., min_length=1, max_length=100, description="Name of the customer")

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class BookingResponse(BaseModel):
    id: int = Field(..., description="Unique booking identifier")
    car_id: int = Field(..., description="ID of the booked car")
    start_date: date = Field(..., description="Booking start date")
    end_date: date = Field(..., description="Booking end date")
    customer_name: str = Field(..., description="Customer name")
