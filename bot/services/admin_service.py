# bot/services/admin_service.py

from utils.database import connect_to_database
from bson import ObjectId
from datetime import datetime, timedelta

async def is_admin(user_id):
    db = await connect_to_database()
    admin = await db.admins.find_one({"user_id": user_id})
    return admin is not None

# Car management functions
async def add_car(brand, model, year, car_type, daily_rate):
    db = await connect_to_database()
    car = {
        "brand": brand,
        "model": model,
        "year": year,
        "type": car_type,
        "daily_rate": daily_rate,
        "status": "available"
    }
    result = await db.cars.insert_one(car)
    return result.inserted_id

async def remove_car(car_id):
    db = await connect_to_database()
    result = await db.cars.delete_one({"_id": ObjectId(car_id)})
    return result.deleted_count > 0

async def update_car(car_id, update_data):
    db = await connect_to_database()
    result = await db.cars.update_one({"_id": ObjectId(car_id)}, {"$set": update_data})
    return result.modified_count > 0

async def list_cars():
    db = await connect_to_database()
    return await db.cars.find().to_list(length=None)

# Booking management functions
async def view_all_bookings(status=None):
    db = await connect_to_database()
    query = {}
    if status:
        query["status"] = status
    return await db.bookings.find(query).to_list(length=None)

async def cancel_booking(booking_id):
    db = await connect_to_database()
    result = await db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
    )
    return result.modified_count > 0

async def modify_booking(booking_id, update_data):
    db = await connect_to_database()
    result = await db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        {"$set": {**update_data, "updated_at": datetime.utcnow()}}
    )
    return result.modified_count > 0

# Report generation functions
async def generate_revenue_report(start_date, end_date):
    db = await connect_to_database()
    pipeline = [
        {
            "$match": {
                "status": "completed",
                "end_date": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_revenue": {"$sum": "$total_price"},
                "booking_count": {"$sum": 1}
            }
        }
    ]
    result = await db.bookings.aggregate(pipeline).to_list(length=1)
    return result[0] if result else {"total_revenue": 0, "booking_count": 0}

async def generate_booking_stats(start_date, end_date):
    db = await connect_to_database()
    pipeline = [
        {
            "$match": {
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }
        }
    ]
    result = await db.bookings.aggregate(pipeline).to_list(length=None)
    return {item["_id"]: item["count"] for item in result}

async def generate_car_utilization_report(start_date, end_date):
    db = await connect_to_database()
    cars = await list_cars()
    utilization = {}
    
    for car in cars:
        bookings = await db.bookings.find({
            "car_id": car["_id"],
            "start_date": {"$lte": end_date},
            "end_date": {"$gte": start_date},
            "status": "completed"
        }).to_list(length=None)
        
        total_days = (end_date - start_date).days + 1
        booked_days = sum((min(booking["end_date"], end_date) - max(booking["start_date"], start_date)).days + 1 for booking in bookings)
        utilization[f"{car['brand']} {car['model']}"] = (booked_days / total_days) * 100

    return utilization