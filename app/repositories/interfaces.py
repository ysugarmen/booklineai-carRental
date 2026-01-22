from __future__ import annotations

from datetime import date
from typing import Optional, Protocol, Sequence, runtime_checkable

from app.models import Booking, Car


@runtime_checkable
class CarRepository(Protocol):
    """
    Abstraction over car persistence.
    """
    def list_all(self) -> Sequence[Car]: ...
    
    def get_by_id(self, car_id: int) -> Optional[Car]: ...


@runtime_checkable
class BookingRepository(Protocol):
    """
    Abstraction over booking persistence.
    """
    def list_all(self) -> Sequence[Booking]: ...
    def list_by_car_id(self, car_id: int) -> Sequence[Booking]: ...
    def list_by_date(self, target_date: date) -> Sequence[Booking]: ...
    def add(self, booking: Booking) -> Booking: ...