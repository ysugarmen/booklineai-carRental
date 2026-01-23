"""
Tests for the BookingService business logic.
"""
from __future__ import annotations

import pytest
from datetime import date
from unittest.mock import MagicMock

from app.models.models import Booking, Car
from app.services.bookings import (
    BookingService,
    BookingConflictError,
    BookingServiceError,
    CarNotFoundError,
)


@pytest.fixture
def mock_car_repository():
    """Create a mock car repository."""
    return MagicMock()


@pytest.fixture
def mock_booking_repository():
    """Create a mock booking repository."""
    return MagicMock()


@pytest.fixture
def booking_service(mock_car_repository, mock_booking_repository):
    """Create a booking service with mocked repositories."""
    return BookingService(
        car_repository=mock_car_repository,
        booking_repository=mock_booking_repository,
    )


class TestAvailableCars:
    """Tests for the available_cars method."""

    def test_returns_all_cars_when_no_bookings(
        self, booking_service, mock_car_repository, mock_booking_repository
    ):
        """Should return all cars when there are no bookings."""
        # Arrange
        cars = [
            Car(id=1, make="Toyota", model="Corolla"),
            Car(id=2, make="Honda", model="Civic"),
        ]
        mock_car_repository.list_all.return_value = cars
        mock_booking_repository.list_by_date.return_value = []
        
        # Act
        result = booking_service.available_cars(target_date=date(2026, 1, 25))
        
        # Assert
        assert len(result) == 2
        assert cars[0] in result
        assert cars[1] in result

    def test_excludes_booked_cars(
        self, booking_service, mock_car_repository, mock_booking_repository
    ):
        """Should exclude cars that are booked on the target date."""
        # Arrange
        cars = [
            Car(id=1, make="Toyota", model="Corolla"),
            Car(id=2, make="Honda", model="Civic"),
        ]
        bookings = [
            Booking(
                id=1,
                car_id=1,
                start_date=date(2026, 1, 24),
                end_date=date(2026, 1, 26),
                customer_name="John",
            )
        ]
        mock_car_repository.list_all.return_value = cars
        mock_booking_repository.list_by_date.return_value = bookings
        
        # Act
        result = booking_service.available_cars(target_date=date(2026, 1, 25))
        
        # Assert
        assert len(result) == 1
        assert result[0].id == 2

    def test_returns_empty_when_no_cars(
        self, booking_service, mock_car_repository
    ):
        """Should return empty list when no cars exist."""
        # Arrange
        mock_car_repository.list_all.return_value = []
        
        # Act
        result = booking_service.available_cars(target_date=date(2026, 1, 25))
        
        # Assert
        assert result == []


class TestCreateBooking:
    """Tests for the create_booking method."""

    def test_creates_booking_successfully(
        self, booking_service, mock_car_repository, mock_booking_repository
    ):
        """Should create a booking when car exists and no conflicts."""
        # Arrange
        car = Car(id=1, make="Toyota", model="Corolla")
        mock_car_repository.get_by_id.return_value = car
        mock_booking_repository.list_by_car_id.return_value = []
        
        expected_booking = Booking(
            id=1,
            car_id=1,
            start_date=date(2026, 1, 25),
            end_date=date(2026, 1, 27),
            customer_name="John Doe",
        )
        mock_booking_repository.add.return_value = expected_booking
        
        # Act
        result = booking_service.create_booking(
            car_id=1,
            start_date=date(2026, 1, 25),
            end_date=date(2026, 1, 27),
            customer_name="John Doe",
        )
        
        # Assert
        assert result.id == 1
        assert result.car_id == 1
        mock_booking_repository.add.assert_called_once()

    def test_raises_error_for_nonexistent_car(
        self, booking_service, mock_car_repository
    ):
        """Should raise CarNotFoundError when car doesn't exist."""
        # Arrange
        mock_car_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(CarNotFoundError) as exc_info:
            booking_service.create_booking(
                car_id=999,
                start_date=date(2026, 1, 25),
                end_date=date(2026, 1, 27),
                customer_name="John Doe",
            )
        
        assert exc_info.value.car_id == 999

    def test_raises_error_for_invalid_date_range(self, booking_service):
        """Should raise BookingServiceError when end_date < start_date."""
        # Act & Assert
        with pytest.raises(BookingServiceError) as exc_info:
            booking_service.create_booking(
                car_id=1,
                start_date=date(2026, 1, 27),
                end_date=date(2026, 1, 25),
                customer_name="John Doe",
            )
        
        assert "before start date" in str(exc_info.value)

    def test_raises_error_for_booking_conflict(
        self, booking_service, mock_car_repository, mock_booking_repository
    ):
        """Should raise BookingConflictError when dates overlap with existing booking."""
        # Arrange
        car = Car(id=1, make="Toyota", model="Corolla")
        existing_booking = Booking(
            id=1,
            car_id=1,
            start_date=date(2026, 1, 24),
            end_date=date(2026, 1, 26),
            customer_name="Existing Customer",
        )
        mock_car_repository.get_by_id.return_value = car
        mock_booking_repository.list_by_car_id.return_value = [existing_booking]
        
        # Act & Assert
        with pytest.raises(BookingConflictError) as exc_info:
            booking_service.create_booking(
                car_id=1,
                start_date=date(2026, 1, 25),
                end_date=date(2026, 1, 28),
                customer_name="John Doe",
            )
        
        assert exc_info.value.car_id == 1


class TestOverlaps:
    """Tests for the _overlaps static method."""

    @pytest.mark.parametrize(
        "start1,end1,start2,end2,expected",
        [
            # Overlapping cases
            (date(2026, 1, 1), date(2026, 1, 10), date(2026, 1, 5), date(2026, 1, 15), True),
            (date(2026, 1, 5), date(2026, 1, 15), date(2026, 1, 1), date(2026, 1, 10), True),
            (date(2026, 1, 1), date(2026, 1, 10), date(2026, 1, 1), date(2026, 1, 10), True),
            (date(2026, 1, 1), date(2026, 1, 10), date(2026, 1, 3), date(2026, 1, 5), True),
            # Non-overlapping cases
            (date(2026, 1, 1), date(2026, 1, 10), date(2026, 1, 11), date(2026, 1, 20), False),
            (date(2026, 1, 11), date(2026, 1, 20), date(2026, 1, 1), date(2026, 1, 10), False),
        ],
    )
    def test_overlaps_detection(self, start1, end1, start2, end2, expected):
        """Should correctly detect overlapping date ranges."""
        result = BookingService._overlaps(start1, end1, start2, end2)
        assert result == expected
