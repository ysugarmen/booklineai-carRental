"""
Tests for the Car Rental API endpoints.
"""
from __future__ import annotations

import pytest
from datetime import date
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.main import create_app
from app.api.deps import get_booking_service
from app.services.bookings import BookingService
from app.models.models import Car, Booking


@pytest.fixture
def mock_booking_service():
    """Create a mock booking service for testing."""
    service = MagicMock(spec=BookingService)
    return service


@pytest.fixture
def client(mock_booking_service):
    """Create a test client with mocked dependencies."""
    app = create_app()
    
    def override_booking_service():
        return mock_booking_service
    
    app.dependency_overrides[get_booking_service] = override_booking_service
    
    with TestClient(app) as test_client:
        yield test_client


class TestGetAvailableCars:
    """Tests for GET /api/cars/available endpoint."""

    def test_get_available_cars_returns_list(self, client, mock_booking_service):
        """Should return a list of available cars for a given date."""
        # Arrange
        target_date = date(2026, 1, 25)
        mock_cars = [
            Car(id=1, make="Toyota", model="Corolla"),
            Car(id=2, make="Honda", model="Civic"),
        ]
        mock_booking_service.available_cars.return_value = mock_cars
        
        # Act
        response = client.get(f"/api/cars/available?date={target_date.isoformat()}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["make"] == "Toyota"
        assert data[1]["make"] == "Honda"
        mock_booking_service.available_cars.assert_called_once_with(target_date=target_date)

    def test_get_available_cars_empty_list(self, client, mock_booking_service):
        """Should return empty list when no cars are available."""
        # Arrange
        target_date = date(2026, 1, 25)
        mock_booking_service.available_cars.return_value = []
        
        # Act
        response = client.get(f"/api/cars/available?date={target_date.isoformat()}")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == []

    def test_get_available_cars_requires_date(self, client):
        """Should return 422 when date parameter is missing."""
        # Act
        response = client.get("/api/cars/available")
        
        # Assert
        assert response.status_code == 422

    def test_get_available_cars_invalid_date_format(self, client):
        """Should return 422 for invalid date format."""
        # Act
        response = client.get("/api/cars/available?date=invalid-date")
        
        # Assert
        assert response.status_code == 422


class TestCreateBooking:
    """Tests for POST /api/bookings endpoint."""

    def test_create_booking_success(self, client, mock_booking_service):
        """Should create a booking successfully."""
        # Arrange
        mock_booking = Booking(
            id=1,
            car_id=1,
            start_date=date(2026, 1, 25),
            end_date=date(2026, 1, 27),
            customer_name="John Doe",
        )
        mock_booking_service.create_booking.return_value = mock_booking
        mock_booking_service.booking_repository.list_all.return_value = []
        
        payload = {
            "car_id": 1,
            "start_date": "2026-01-25",
            "end_date": "2026-01-27",
            "customer_name": "John Doe",
        }
        
        # Act
        response = client.post("/api/bookings", json=payload)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["car_id"] == 1
        assert data["customer_name"] == "John Doe"

    def test_create_booking_car_not_found(self, client, mock_booking_service):
        """Should return 404 when car does not exist."""
        from app.services.bookings import CarNotFoundError
        
        # Arrange
        mock_booking_service.booking_repository.list_all.return_value = []
        mock_booking_service.create_booking.side_effect = CarNotFoundError(car_id=999)
        
        payload = {
            "car_id": 999,
            "start_date": "2026-01-25",
            "end_date": "2026-01-27",
            "customer_name": "John Doe",
        }
        
        # Act
        response = client.post("/api/bookings", json=payload)
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_booking_conflict(self, client, mock_booking_service):
        """Should return 409 when booking conflicts with existing booking."""
        from app.services.bookings import BookingConflictError
        
        # Arrange
        mock_booking_service.booking_repository.list_all.return_value = []
        mock_booking_service.create_booking.side_effect = BookingConflictError(
            car_id=1,
            start_date=date(2026, 1, 25),
            end_date=date(2026, 1, 27),
        )
        
        payload = {
            "car_id": 1,
            "start_date": "2026-01-25",
            "end_date": "2026-01-27",
            "customer_name": "John Doe",
        }
        
        # Act
        response = client.post("/api/bookings", json=payload)
        
        # Assert
        assert response.status_code == 409
        assert "conflict" in response.json()["detail"].lower()

    def test_create_booking_invalid_dates(self, client, mock_booking_service):
        """Should return 422 when end_date is before start_date."""
        from app.services.bookings import BookingServiceError
        
        # Arrange
        mock_booking_service.booking_repository.list_all.return_value = []
        mock_booking_service.create_booking.side_effect = BookingServiceError(
            "End date cannot be before start date."
        )
        
        payload = {
            "car_id": 1,
            "start_date": "2026-01-27",
            "end_date": "2026-01-25",
            "customer_name": "John Doe",
        }
        
        # Act
        response = client.post("/api/bookings", json=payload)
        
        # Assert
        assert response.status_code == 422

    def test_create_booking_missing_fields(self, client):
        """Should return 422 when required fields are missing."""
        # Act
        response = client.post("/api/bookings", json={})
        
        # Assert
        assert response.status_code == 422

    def test_create_booking_empty_customer_name(self, client):
        """Should return 422 when customer_name is empty."""
        payload = {
            "car_id": 1,
            "start_date": "2026-01-25",
            "end_date": "2026-01-27",
            "customer_name": "",
        }
        
        # Act
        response = client.post("/api/bookings", json=payload)
        
        # Assert
        assert response.status_code == 422
