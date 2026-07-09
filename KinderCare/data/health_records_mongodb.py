"""
Health Records MongoDB Database Management

This module manages the MongoDB database for storing child health records.
Each collection represents a child's health timeline with documents as individual health events.

Collection naming format: {user_id}_{child_name}
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import os


class HealthRecordsDB:
    """Manages MongoDB health records database operations."""
    
    def __init__(self, db_name="health_records_database", uri="mongodb://localhost:27017/"):
        """
        Initialize MongoDB connection and database.
        
        Args:
            db_name (str): Name of the database
            uri (str): MongoDB connection URI
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.db_name = db_name
        
    def create_child_timeline(self, user_id, child_name):
        """
        Create a new collection for a child's health timeline.
        
        Args:
            user_id (str): Unique identifier for the user/parent
            child_name (str): Name of the child
            
        Returns:
            str: Collection name in format {user_id}_{child_name}
        """
        collection_name = f"{user_id}_{child_name}"
        collection = self.db[collection_name]
        
        # Create a simple document to initialize the collection
        if collection.count_documents({}) == 0:
            collection.insert_one({
                "initialized": True,
                "created_at": datetime.now(),
                "child_name": child_name,
                "user_id": user_id
            })
            collection.delete_one({"initialized": True})
        
        return collection_name
    
    def add_health_event(self, user_id, child_name, event_data):
        """
        Add a health event document to a child's timeline.
        
        Args:
            user_id (str): Unique identifier for the user/parent
            child_name (str): Name of the child
            event_data (dict): Health event information including:
                - event_type: Type of health event (e.g., 'vaccination', 'illness', 'checkup')
                - description: Details about the event
                - date: Date of the event
                - notes: Additional notes (optional)
                
        Returns:
            str: Inserted document ID
        """
        collection_name = f"{user_id}_{child_name}"
        collection = self.db[collection_name]
        
        # Ensure required fields
        if 'timestamp' not in event_data:
            event_data['timestamp'] = datetime.now()
        
        result = collection.insert_one(event_data)
        return str(result.inserted_id)
    
    def get_health_timeline(self, user_id, child_name, limit=None):
        """
        Retrieve all health events for a child.
        
        Args:
            user_id (str): Unique identifier for the user/parent
            child_name (str): Name of the child
            limit (int): Maximum number of events to retrieve (None for all)
            
        Returns:
            list: List of health event documents
        """
        collection_name = f"{user_id}_{child_name}"
        collection = self.db[collection_name]
        
        query = collection.find().sort("timestamp", -1)
        if limit:
            query = query.limit(limit)
        
        return list(query)
    
    def get_recent_events(self, user_id, child_name, days=30):
        """
        Get health events from the last N days.
        
        Args:
            user_id (str): Unique identifier for the user/parent
            child_name (str): Name of the child
            days (int): Number of days to look back
            
        Returns:
            list: Health event documents from recent days
        """
        collection_name = f"{user_id}_{child_name}"
        collection = self.db[collection_name]
        
        cutoff_date = datetime.now() - timedelta(days=days)
        events = collection.find({"timestamp": {"$gte": cutoff_date}}).sort("timestamp", -1)
        
        return list(events)
    
    def delete_health_event(self, user_id, child_name, event_id):
        """
        Delete a specific health event.
        
        Args:
            user_id (str): Unique identifier for the user/parent
            child_name (str): Name of the child
            event_id (str): MongoDB ObjectId of the event
            
        Returns:
            bool: True if event was deleted, False otherwise
        """
        from bson import ObjectId
        
        collection_name = f"{user_id}_{child_name}"
        collection = self.db[collection_name]
        
        result = collection.delete_one({"_id": ObjectId(event_id)})
        return result.deleted_count > 0
    
    def update_health_event(self, user_id, child_name, event_id, update_data):
        """
        Update a health event document.
        
        Args:
            user_id (str): Unique identifier for the user/parent
            child_name (str): Name of the child
            event_id (str): MongoDB ObjectId of the event
            update_data (dict): Fields to update
            
        Returns:
            bool: True if event was updated, False otherwise
        """
        from bson import ObjectId
        
        collection_name = f"{user_id}_{child_name}"
        collection = self.db[collection_name]
        
        result = collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def get_all_children(self, user_id):
        """
        Get all children for a user.
        
        Args:
            user_id (str): Unique identifier for the user/parent
            
        Returns:
            list: List of child names
        """
        children = []
        for collection_name in self.db.list_collection_names():
            if collection_name.startswith(user_id + "_"):
                child_name = collection_name.replace(user_id + "_", "")
                children.append(child_name)
        
        return children
    
    def close(self):
        """Close the database connection."""
        self.client.close()


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = HealthRecordsDB()
    
    # Create a child's health timeline
    user_id = "user123"
    child_name = "Alice"
    collection = db.create_child_timeline(user_id, child_name)
    print(f"Created collection: {collection}")
    
    # Add a health event
    event = {
        "event_type": "vaccination",
        "vaccine_name": "MMR",
        "description": "First dose of MMR vaccine",
        "date": "2025-12-21",
        "notes": "No adverse reactions"
    }
    event_id = db.add_health_event(user_id, child_name, event)
    print(f"Added health event: {event_id}")
    
    # Retrieve timeline
    timeline = db.get_health_timeline(user_id, child_name)
    print(f"Health timeline: {timeline}")
    
    # Close connection
    db.close()
