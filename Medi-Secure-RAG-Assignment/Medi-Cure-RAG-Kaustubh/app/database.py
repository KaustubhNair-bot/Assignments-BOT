"""
MongoDB Database Module
Handles MongoDB connection and operations for storing medical transcriptions
"""
import os
from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from app.config import settings


class MongoDBManager:
    """
    MongoDB Manager for medical transcription storage
    Stores documents, metadata, and user information
    """
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self._connected = False
    
    def connect(self):
        """Connect to MongoDB"""
        if self._connected:
            return
        
        try:
            self.client = MongoClient(settings.MONGODB_URL)
            self.db = self.client[settings.MONGODB_DATABASE]
            
            # Test connection
            self.client.admin.command('ping')
            self._connected = True
            print(f"Connected to MongoDB: {settings.MONGODB_DATABASE}")
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            print("Falling back to file-based storage for users...")
            self._connected = False
    
    def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        return self._connected
    
    def get_collection(self, name: str) -> Optional[Collection]:
        """Get a collection from the database"""
        if not self._connected:
            return None
        return self.db[name]
    
    @property
    def transcriptions(self) -> Optional[Collection]:
        """Get the transcriptions collection"""
        return self.get_collection("transcriptions")
    
    @property
    def users(self) -> Optional[Collection]:
        """Get the users collection"""
        return self.get_collection("users")
    
    def insert_transcription(self, doc: Dict[str, Any]) -> Optional[str]:
        """Insert a transcription document"""
        if not self._connected:
            return None
        result = self.transcriptions.insert_one(doc)
        return str(result.inserted_id)
    
    def insert_many_transcriptions(self, docs: List[Dict[str, Any]]) -> int:
        """Insert multiple transcription documents"""
        if not self._connected or not docs:
            return 0
        result = self.transcriptions.insert_many(docs)
        return len(result.inserted_ids)
    
    def get_transcription_by_case_id(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get a transcription by case ID"""
        if not self._connected:
            return None
        return self.transcriptions.find_one({"case_id": case_id})
    
    def get_transcriptions_by_ids(self, case_ids: List[str]) -> List[Dict[str, Any]]:
        """Get multiple transcriptions by case IDs"""
        if not self._connected:
            return []
        cursor = self.transcriptions.find({"case_id": {"$in": case_ids}})
        return list(cursor)
    
    def get_all_specialties(self) -> List[str]:
        """Get all unique medical specialties"""
        if not self._connected:
            return []
        specialties = self.transcriptions.distinct("specialty")
        return sorted([s for s in specialties if s and s != 'nan'])
    
    def count_transcriptions(self) -> int:
        """Count total transcriptions"""
        if not self._connected:
            return 0
        return self.transcriptions.count_documents({})
    
    def clear_transcriptions(self):
        """Clear all transcriptions (for rebuilding)"""
        if self._connected:
            self.transcriptions.delete_many({})
    
    # User operations
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        if not self._connected:
            return None
        return self.users.find_one({"username": username})
    
    def create_user(self, user_data: Dict[str, Any]) -> bool:
        """Create a new user"""
        if not self._connected:
            return False
        
        if self.users.find_one({"username": user_data["username"]}):
            return False
        
        self.users.insert_one(user_data)
        return True
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self._connected = False


# Global MongoDB manager instance
mongodb = MongoDBManager()
