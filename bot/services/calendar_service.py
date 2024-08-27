# bot/services/calendar_service.py

from utils.database import connect_to_database
from datetime import datetime, timedelta

async def get_available_dates(start_date=None, end_date=None, car_type=None):
    if not start_date:
        start_date = datetime.now().date()
    if not end_date:
        end_date = start_date + timedelta(days=30)

    db = await connect_to_database()
    
    # Get all bookings within the date range
    bookings_query = {
        "pickup_date": {"$lte": end_date},
        "return_date": {"$gte": start_date},
        "status": {"$in": ["pending", "confirmed"]}
    }
    if car_type:
        bookings_query["car_type"] = car_type

    bookings = await db.bookings.find(bookings_query).to_list(length=None)

    # Get all cars
    cars_query = {"status": "active"}
    if car_type:
        cars_query["type"] = car_type
    cars = await db.cars.find(cars_query).to_list(length=None)

    available_dates = {}
    current_date = start_date
    while current_date <= end_date:
        available_cars = len(cars)
        for booking in bookings:
            if booking["pickup_date"] <= current_date <= booking["return_date"]:
                available_cars -= 1
        
        if available_cars > 0:
            available_dates[current_date] = available_cars
        
        current_date += timedelta(days=1)

    return available_dates

async def check_date_range_availability(start_date, end_date, car_type=None):
    available_dates = await get_available_dates(start_date, end_date, car_type)
    return all(date in available_dates for date in daterange(start_date, end_date))

async def block_dates(booking_id, start_date, end_date, car_type):
    db = await connect_to_database()
    await db.bookings.update_one(
        {"_id": booking_id},
        {"$set": {
            "pickup_date": start_date,
            "return_date": end_date,
            "car_type": car_type,
            "status": "confirmed"
        }}
    )

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)