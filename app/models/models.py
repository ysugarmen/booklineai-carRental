from __future__ import annotations

from datetime import date
from pydantic import BaseModel, ConfigDict, Field


class Car(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int = Field(..., description="Unique identifier for the car")
    make: str = Field(..., description="Manufacturer of the car")
    model: str = Field(..., description="Model of the car")


class Booking(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int = Field(..., description="Unique identifier for the booking")
    car_id: int = Field(..., description="Identifier of the booked car")
    start_date: date = Field(..., description="Start date of the booking")
    end_date: date = Field(..., description="End date of the booking")
    customer_name: str = Field(..., description="Name of the customer who made the booking")

