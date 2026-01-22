from fastapi import APIRouter

from app.api.routes import bookings, cars

api_router = APIRouter()
api_router.include_router(bookings.router)
api_router.include_router(cars.router)