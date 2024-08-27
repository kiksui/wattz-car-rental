# bot/utils/database.py

import motor.motor_asyncio
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

async def connect_to_database():
    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client.wattz_car_rental
    return db

# Synchronous connection for admin tasks
def get_sync_db():
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client.wattz_car_rental
    return db