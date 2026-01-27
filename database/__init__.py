# Database package
from database.connection import init_db
from database.models import UserDocument, MessageDocument

__all__ = ["init_db", "UserDocument", "MessageDocument"]
