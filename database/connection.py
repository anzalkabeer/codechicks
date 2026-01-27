"""
MongoDB Connection Module

Provides database initialization and connection management using Beanie ODM.
"""

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB client instance (reusable)
_client: AsyncIOMotorClient = None


async def init_db():
    """
    Initialize MongoDB connection and Beanie ODM.
    
    Call this during application startup (lifespan event).
    """
    global _client
    
    # Import models here to avoid circular imports
    from database.models import UserDocument, MessageDocument
    
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
    database_name = os.getenv("DATABASE_NAME", "codechicks")
    
    _client = AsyncIOMotorClient(mongodb_uri)
    
    await init_beanie(
        database=_client[database_name],
        document_models=[UserDocument, MessageDocument]
    )
    
    print(f"✅ Connected to MongoDB: {database_name}")


async def close_db():
    """
    Close MongoDB connection.
    
    Call this during application shutdown (lifespan event).
    """
    global _client
    if _client:
        _client.close()
        print("🔌 MongoDB connection closed")


def get_client() -> AsyncIOMotorClient:
    """Get the MongoDB client instance."""
    return _client
