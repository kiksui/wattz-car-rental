# bot/services/booking_service.py

from utils.database import connect_to_database
from bson import ObjectId
from datetime import datetime, timedelta
from services.car_service import get_car_price
from services.calendar_service import check_date_range_availability

class BookingError(Exception):
    pass

async def check_car_availability(car_id, start_date, end_date):
    db = await connect_to_database()
    car = await db.cars.find_one({"_id": ObjectId(car_id)})
    if not car:
        raise BookingError("Car not found")
    
    overlapping_bookings = await db.bookings.count_documents({
        "car_id": car_id,
        "status": {"$in": ["pending", "confirmed"]},
        "$or": [
            {"start_date": {"$lt": end_date}, "end_date": {"$gt": start_date}},
            {"start_date": {"$gte": start_date, "$lt": end_date}},
            {"end_date": {"$gt": start_date, "$lte": end_date}}
        ]
    })
    
    return overlapping_bookings == 0

async def create_booking(user_id, car_id, start_date, end_date, pickup_location, dropoff_location):
    db = await connect_to_database()

    # Validate dates
    if start_date >= end_date:
        raise BookingError("Start date must be before end date")

    # Check availability
    if not await check_car_availability(car_id, start_date, end_date):
        raise BookingError("Selected dates are not available for this car")

    # Get car details
    car = await db.cars.find_one({"_id": ObjectId(car_id)})
    if not car:
        raise BookingError("Car not found")

    # Calculate total price
    days = (end_date - start_date).days + 1
    total_price = days * car['daily_rate']

    booking = {
        "user_id": user_id,
        "car_id": car_id,
        "start_date": start_date,
        "end_date": end_date,
        "pickup_location": pickup_location,
        "dropoff_location": dropoff_location,
        "total_price": total_price,
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    result = await db.bookings.insert_one(booking)
    booking['_id'] = result.inserted_id

    return booking

async def get_booking(booking_id):
    db = await connect_to_database()
    booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        raise BookingError("Booking not found")
    return booking

async def update_booking_status(booking_id, new_status, additional_data=None):
    db = await connect_to_database()
    update_data = {"status": new_status, "updated_at": datetime.utcnow()}
    if additional_data:
        update_data.update(additional_data)
    
    result = await db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise BookingError("Booking not found or status not updated")
    return True

async def cancel_booking(booking_id):
    booking = await get_booking(booking_id)
    if booking['status'] not in ['pending', 'confirmed']:
        raise BookingError("Cannot cancel a booking that is not pending or confirmed")
    
    return await update_booking_status(booking_id, 'cancelled')

async def get_user_bookings(user_id, status=None):
    db = await connect_to_database()
    query = {"user_id": user_id}
    if status:
        query["status"] = status
    return await db.bookings.find(query).to_list(length=None)

async def get_upcoming_bookings(days=7):
    db = await connect_to_database()
    end_date = datetime.utcnow() + timedelta(days=days)
    query = {
        "start_date": {"$lte": end_date},
        "end_date": {"$gte": datetime.utcnow()},
        "status": "confirmed"
    }
    return await db.bookings.find(query).to_list(length=None)