from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Sequence

from app.models.models import Booking, Car
from app.repositories.interfaces import BookingRepository, CarRepository


class BookingServiceError(Exception):
    """Base class for BookingService exceptions."""


class CarNotFoundError(BookingServiceError):
    """Raised when a car is not found in the repository."""
    def __init__(self, car_id: int) -> None:
        super().__init__(f"Car with ID {car_id} not found.")
        self.car_id = car_id


class BookingConflictError(BookingServiceError):
    """Raised when a booking conflicts with existing bookings."""
    def __init__(self, car_id: int, start_date: date, end_date: date) -> None:
        super().__init__(
            f"Booking conflict for car ID {car_id} from {start_date} to {end_date}."
        )
        self.car_id = car_id
        self.start_date = start_date
        self.end_date = end_date


@dataclass(frozen=True, slots=True)
class BookingService:
    """
    Business logic for managing bookings & availability.
    """
    car_repository: CarRepository
    booking_repository: BookingRepository

    def available_cars(self, target_date: date) -> Sequence[Car]:
        cars = list(self.car_repository.list_all())
        if not cars:
            return []
        
        booked_car_ids = {
            booking.car_id for booking in self.booking_repository.list_by_date(target_date)
            if self._covers_date(booking, target_date)
        }

        return [car for car in cars if car.id not in booked_car_ids]
    

    def create_booking(self, *, car_id: int, start_date: date, end_date: date, customer_name: str, booking_id: int) -> Booking:
        if end_date < start_date:
            raise BookingServiceError("End date cannot be before start date.")
        
        car = self.car_repository.get_by_id(car_id)
        if car is None:
            raise CarNotFoundError(car_id)
        
        if self._has_booking_conflict(car_id=car_id, start_date=start_date, end_date=end_date):
            raise BookingConflictError(car_id, start_date, end_date)

        new_booking = Booking(
            id=booking_id,
            car_id=car_id,
            start_date=start_date,
            end_date=end_date,
            customer_name=customer_name
        )
        return self.booking_repository.add(new_booking)
    

    # -------- Private Helpers --------
    def _has_booking_conflict(self, *, car_id: int, start_date: date, end_date: date) -> bool:
        existing_bookings = self.booking_repository.list_by_car_id(car_id)
        for booking in existing_bookings:
            if self._overlaps(booking.start_date, booking.end_date, start_date, end_date):
                return True
        return False
    

    @staticmethod
    def _overlaps(start1: date, end1: date, start2: date, end2: date) -> bool:
        return not (end1 < start2 or end2 < start1)


    @staticmethod
    def _covers_date(booking: Booking, target_date: date) -> bool:
        return booking.start_date <= target_date <= booking.end_date