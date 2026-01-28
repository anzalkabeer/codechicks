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
    
    try:
        # Add serverSelectionTimeoutMS for faster failure detection
        _client = AsyncIOMotorClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # Test the connection
        await _client.admin.command('ping')
        
        await init_beanie(
            database=_client[database_name],
            document_models=[UserDocument, MessageDocument]
        )
        
        print(f"✅ Connected to MongoDB: {database_name}")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        # Re-raise to let the app know about the failure
        raise


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
