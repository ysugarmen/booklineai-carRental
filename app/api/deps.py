from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.repositories.file_json import FileBookingRepository, FileCarRepository
from app.infra.storage.json_store import JsonStore
from app.services.bookings import BookingService

settings = get_settings()

@lru_cache(maxsize=1)
def _json_store() -> JsonStore:
    """
    Single JsonStore instance per process.
    Uses settings for data file location.
    """
    return JsonStore(path=settings.DATA_FILE_PATH)


@lru_cache(maxsize=1)
def _car_repository() -> FileCarRepository:
    """
    Single CarRepository instance per process.
    """
    return FileCarRepository(json_store=_json_store())


@lru_cache(maxsize=1)
def _booking_repository() -> FileBookingRepository:
    """
    Single BookingRepository instance per process.
    """
    return FileBookingRepository(json_store=_json_store())


def get_booking_service() -> BookingService:
    """
    BookingService dependency.
    """
    return BookingService(
        car_repository=_car_repository(),
        booking_repository=_booking_repository(),
    )