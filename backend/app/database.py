# Database connection and setup
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    mongodb.client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    mongodb.database = mongodb.client[os.getenv("DATABASE_NAME")]
    logger.info("Connected to MongoDB")

async def close_mongo_connection():
    """Close database connection"""
    mongodb.client.close()
    logger.info("Disconnected from MongoDB")

async def save_case(case_data: dict):
    """Save case to database"""
    case_data["created_at"] = datetime.utcnow()
    result = await mongodb.database[os.getenv("COLLECTION_NAME")].insert_one(case_data)
    return str(result.inserted_id)

async def get_case(case_id: str):
    """Retrieve case from database"""
    from bson import ObjectId
    case = await mongodb.database[os.getenv("COLLECTION_NAME")].find_one({"_id": ObjectId(case_id)})
    if case:
        case["_id"] = str(case["_id"])
    return case

async def get_all_cases():
    """Retrieve all cases"""
    cases = []
    async for case in mongodb.database[os.getenv("COLLECTION_NAME")].find():
        case["_id"] = str(case["_id"])
        cases.append(case)
    return cases
