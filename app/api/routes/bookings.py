from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_booking_service
from app.api.schemas import BookingResponse, CreateBookingRequest
from app.core.logging import get_logger
from app.services.bookings import (
    BookingConflictError,
    BookingService,
    CarNotFoundError,
    BookingServiceError,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: CreateBookingRequest,
    service: BookingService = Depends(get_booking_service),
) -> BookingResponse:
    """
    Create a new booking for a car.
    
    - **car_id**: ID of the car to book
    - **start_date**: Booking start date (YYYY-MM-DD)
    - **end_date**: Booking end date (YYYY-MM-DD)  
    - **customer_name**: Name of the customer
    """
    logger.info(
        "Booking attempt: car_id=%d, dates=%s to %s, customer=%s",
        payload.car_id,
        payload.start_date,
        payload.end_date,
        payload.customer_name,
    )
    try:
        booking = service.create_booking(
            car_id=payload.car_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            customer_name=payload.customer_name,
        )
        logger.info(
            "Booking successful: booking_id=%d, car_id=%d, customer=%s",
            booking.id,
            booking.car_id,
            booking.customer_name,
        )
        return BookingResponse.model_validate(booking.model_dump())
    
    except CarNotFoundError as e:
        logger.warning("Booking failed - car not found: car_id=%d", payload.car_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e

    except BookingConflictError as e:
        logger.warning(
            "Booking failed - conflict: car_id=%d, dates=%s to %s",
            payload.car_id,
            payload.start_date,
            payload.end_date,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e

    except BookingServiceError as e:
        logger.error("Booking failed - service error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e