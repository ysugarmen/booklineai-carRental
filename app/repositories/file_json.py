from __future__ import annotations

from datetime import date
from typing import List, Optional, Sequence

from app.infra.storage.json_store import JsonStore
from app.models import Booking, Car

class FileCarRepository:
    """
    JSON-backed repository for Cars.
    """
    def __init__(self, json_store: JsonStore):
        self._json_store = json_store
    

    def list_all(self) -> Sequence[Car]:
        cars_data = self._json_store.read()
        cars_raw = cars_data.get("cars", [])
        return [Car.model_validate(car) for car in cars_raw]


    def get_by_id(self, car_id: int) -> Optional[Car]:
        data = self._json_store.read()
        for car in data.get("cars", []):
            if car["id"] == car_id:
                return Car.model_validate(car)
        return None


class FileBookingRepository:
    """
    JSON-backed repository for Bookings.
    """
    def __init__(self, json_store: JsonStore):
        self._json_store = json_store
    

    def list_all(self) -> Sequence[Booking]:
        bookings_data = self._json_store.read()
        bookings_raw = bookings_data.get("bookings", [])
        return [Booking.model_validate(booking) for booking in bookings_raw]
    
    def list_by_car_id(self, car_id: int) -> Sequence[Booking]:
        bookings_data = self._json_store.read()
        bookings_raw = bookings_data.get("bookings", [])
        return [
            Booking.model_validate(booking)
            for booking in bookings_raw
            if booking["car_id"] == car_id
        ]

    def list_by_dates(self, target_date: date) -> Sequence[Booking]:
        bookings_data = self._json_store.read()
        target_date_str = target_date.isoformat()
        bookings: List[Booking] = []

        for booking in bookings_data.get("bookings", []):
            if booking["start_date"] <= target_date_str <= booking["end_date"]:
                bookings.append(Booking.model_validate(booking))
        return bookings

    def add(self, booking: Booking) -> Booking:
        def _append_booking(data: dict) -> dict:
            bookings = data.setdefault("bookings", [])
            bookings.append(booking.model_dump(mode="json"))
            return data
        
        self._json_store.update(_append_booking)
        return booking
        