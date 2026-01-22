from __future__ import annotations

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_booking_service
from app.core.logging import get_logger
from app.models.models import Car
from app.services.bookings import BookingService

logger = get_logger(__name__)

router = APIRouter(prefix="/cars", tags=["cars"])


@router.get("/available", response_model=List[Car])
def get_available_cars(
    date: date = Query(..., description="Target date (YYYY-MM-DD) to check car availability."),
    service: BookingService = Depends(get_booking_service),
) -> List[Car]:
    """
    Retrieve a list of cars available for booking on a specific date.
    """
    logger.info("Querying available cars for date: %s", date)
    available_cars = service.available_cars(target_date=date)
    logger.info("Found %d available cars for date %s", len(available_cars), date)
    return list(available_cars)