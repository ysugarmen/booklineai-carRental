# BookLineAI Car Rental Service

A REST API for a car rental service built with **FastAPI**, featuring car availability queries and booking management.

## 🎯 Features

- **List Available Cars**: Query cars available for a specific date
- **Create Bookings**: Book a car for a date range
- **Date Conflict Detection**: Prevents double-booking of vehicles
- **File-based Storage**: JSON file persistence (easily upgradable to database)
- **Structured Logging**: Comprehensive logging for debugging and monitoring

---

## 🏗️ Architecture & Design Choices

### Project Structure

```
app/
├── main.py              # FastAPI application factory & lifespan
├── api/
│   ├── deps.py          # Dependency injection configuration
│   ├── schemas.py       # Pydantic request/response models
│   └── routes/          # API endpoint definitions
├── core/
│   ├── config.py        # Application settings (pydantic-settings)
│   └── logging.py       # Logging configuration
├── models/
│   └── models.py        # Domain models (Car, Booking)
├── repositories/
│   ├── interfaces.py    # Repository protocols (abstractions)
│   └── file_json.py     # JSON file implementations
├── services/
│   └── bookings.py      # Business logic layer
└── infra/
    └── storage/
        └── json_store.py # Atomic JSON file operations
```

### Design Principles

1. **Clean Architecture**: The codebase follows a layered architecture:
   - **Routes** → Handle HTTP concerns (validation, status codes)
   - **Services** → Contain business logic (availability, conflict detection)
   - **Repositories** → Abstract data access (easily swap JSON for database)

2. **Dependency Injection**: FastAPI's `Depends` mechanism allows:
   - Easy testing with mocked dependencies
   - Single source of truth for service instantiation
   - Future-proof for database migration

3. **Repository Pattern**: Protocol-based interfaces in `repositories/interfaces.py` allow:
   - Swapping storage backends without changing business logic
   - Clear contracts for data operations

4. **Immutable Models**: Using Pydantic's `frozen=True` ensures domain objects are immutable, preventing accidental state mutations.

5. **Atomic File Operations**: The `JsonStore` class uses:
   - Temporary files + `os.replace()` for atomic writes
   - File-based locking for cross-process safety
   - Thread locks for in-process safety

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip or uv package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd booklineai-carRental
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

### API Documentation

FastAPI provides interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📖 API Endpoints

### List Available Cars

**GET** `/api/cars/available`

Query cars available on a specific date.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | string (YYYY-MM-DD) | Yes | Target date to check availability |

**Example Request**:
```bash
curl "http://localhost:8000/api/cars/available?date=2026-01-25"
```

**Example Response**:
```json
[
  {"id": 1, "make": "Toyota", "model": "Corolla"},
  {"id": 2, "make": "Honda", "model": "Civic"}
]
```

---

### Create Booking

**POST** `/api/bookings`

Create a new car booking.

**Request Body**:
```json
{
  "car_id": 1,
  "start_date": "2026-01-25",
  "end_date": "2026-01-27",
  "customer_name": "John Doe"
}
```

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/bookings" \
  -H "Content-Type: application/json" \
  -d '{"car_id": 1, "start_date": "2026-01-25", "end_date": "2026-01-27", "customer_name": "John Doe"}'
```

**Response Codes**:
| Code | Description |
|------|-------------|
| 201 | Booking created successfully |
| 404 | Car not found |
| 409 | Booking conflict (car already booked for dates) |
| 422 | Validation error (invalid dates, missing fields) |

---

## 🧪 Testing

The project includes comprehensive unit tests for both API endpoints and business logic.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing
```

### Test Structure

```
tests/
├── test_api.py       # API endpoint tests (integration)
└── test_services.py  # Business logic tests (unit)
```

### Test Coverage

- **API Tests**: Covers successful operations, error cases, validation
- **Service Tests**: Covers business logic, date overlap detection, edge cases

---

## 📋 Logging

The application logs key events to stdout:

### Logged Events

| Event | Level | Description |
|-------|-------|-------------|
| Car availability query | INFO | Logs date queried and number of available cars |
| Booking attempt | INFO | Logs booking request details |
| Booking success | INFO | Logs successful booking creation |
| Car not found | WARNING | Logs when booking fails due to missing car |
| Booking conflict | WARNING | Logs when dates conflict with existing booking |
| Service error | ERROR | Logs unexpected service-level errors |

### Example Log Output

```
2026-01-22 10:30:45 - app.api.routes.cars - INFO - Querying available cars for date: 2026-01-25
2026-01-22 10:30:45 - app.api.routes.cars - INFO - Found 5 available cars for date 2026-01-25
2026-01-22 10:31:12 - app.api.routes.bookings - INFO - Booking attempt: car_id=1, dates=2026-01-25 to 2026-01-27, customer=John Doe
2026-01-22 10:31:12 - app.api.routes.bookings - INFO - Booking successful: booking_id=1, car_id=1, customer=John Doe
```

---

## 🐳 Docker (Optional)

### Build the Image

```bash
docker build -t car-rental-api .
```

### Run the Container

```bash
docker run -p 8000:8000 car-rental-api
```

### Using Docker Compose

```bash
docker-compose up
```

---

## 📁 Data Storage

The application uses a JSON file for data persistence:

- **Location**: `storage/data.json`
- **Structure**:
  ```json
  {
    "cars": [...],
    "bookings": [...]
  }
  ```

### Initial Data

The repository includes sample car data. To reset:
```bash
# Copy the sample data
cp storage/data.json.example storage/data.json
```

---

## 🔮 Future Improvements

1. **Database Integration**: Replace JSON storage with PostgreSQL/SQLite
2. **Authentication**: Add user authentication and authorization
3. **Car Categories**: Add vehicle types, pricing tiers
4. **Pagination**: Add pagination for large datasets
5. **Cancellation**: Add booking cancellation endpoint
6. **Date Validation**: Prevent bookings in the past

---

## 📜 License

This project is created as part of a technical assessment.
