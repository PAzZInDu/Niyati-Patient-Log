from supabase import create_client, Client
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import json

class SupabaseManager:
    def __init__(self, url: str, key: str):
        """
        Initialize Supabase client
        
        Args:
            url (str): Supabase project URL
            key (str): Supabase service role or anon key
        """
        self.url = url
        self.key = key
        self.supabase = create_client(url, key)
    
    # User Operations
    def create_user_profile(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update user profile in Supabase
        
        Args:
            user_data (dict): User profile data
            
        Returns:
            dict: Created/updated user profile
        """
        # Check if user already exists
        existing_user = self.supabase.table('user_profiles')\
            .select('*')\
            .eq('email', user_data.get('email'))\
            .execute()
            
        user_data['updated_at'] = datetime.utcnow().isoformat()
        
        if existing_user.data:
            # Update existing user
            response = self.supabase.table('user_profiles')\
                .update(user_data)\
                .eq('email', user_data.get('email'))\
                .execute()
        else:
            # Create new user
            user_data['created_at'] = datetime.utcnow().isoformat()
            response = self.supabase.table('user_profiles')\
                .insert(user_data)\
                .execute()
                
        return response.data[0] if response.data else None
    
    def get_user_profile(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile by email
        
        Args:
            email (str): User's email
            
        Returns:
            dict: User profile or None if not found
        """
        response = self.supabase.table('user_profiles')\
            .select('*')\
            .eq('email', email)\
            .execute()
        return response.data[0] if response.data else None
    
    # Daily Log Operations
    def create_daily_log(self, user_email: str, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new daily log entry
        
        Args:
            user_email (str): Email of the user creating the log
            log_data (dict): Log data to be saved
            
        Returns:
            dict: Created log entry
        """
        log_data['user_email'] = user_email
        log_data['created_at'] = datetime.utcnow().isoformat()
        
        response = self.supabase.table('daily_logs')\
            .insert(log_data)\
            .execute()
            
        return response.data[0] if response.data else None
    
    def get_user_logs(self, user_email: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        Get logs for a user within a date range
        
        Args:
            user_email (str): User's email
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            list: List of log entries
        """
        query = self.supabase.table('daily_logs')\
            .select('*')\
            .eq('user_email', user_email)
            
        if start_date:
            query = query.gte('date', start_date)
        if end_date:
            query = query.lte('date', end_date)
            
        response = query.order('date', desc=True).execute()
        return response.data if response.data else []
    
    def delete_log(self, log_id: str) -> bool:
        """
        Delete a log entry
        
        Args:
            log_id (str): ID of the log to delete
            
        Returns:
            bool: True if deletion was successful
        """
        response = self.supabase.table('daily_logs')\
            .delete()\
            .eq('id', log_id)\
            .execute()
        return len(response.data) > 0
    
    # Reminder Operations
    def create_reminder(self, user_email: str, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new reminder
        
        Args:
            user_email (str): Email of the user
            reminder_data (dict): Reminder data
            
        Returns:
            dict: Created reminder
        """
        reminder_data['user_email'] = user_email
        reminder_data['created_at'] = datetime.utcnow().isoformat()
        
        response = self.supabase.table('reminders')\
            .insert(reminder_data)\
            .execute()
            
        return response.data[0] if response.data else None
    
    def get_user_reminders(self, user_email: str) -> List[Dict[str, Any]]:
        """
        Get all reminders for a user
        
        Args:
            user_email (str): User's email
            
        Returns:
            list: List of reminders
        """
        response = self.supabase.table('reminders')\
            .select('*')\
            .eq('user_email', user_email)\
            .order('date')\
            .order('time')\
            .execute()
        return response.data if response.data else []
    
    def update_reminder(self, reminder_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a reminder
        
        Args:
            reminder_id (str): ID of the reminder to update
            updates (dict): Fields to update
            
        Returns:
            dict: Updated reminder or None if not found
        """
        updates['updated_at'] = datetime.utcnow().isoformat()
        
        response = self.supabase.table('reminders')\
            .update(updates)\
            .eq('id', reminder_id)\
            .execute()
            
        return response.data[0] if response.data else None
    
    def delete_reminder(self, reminder_id: str) -> bool:
        """
        Delete a reminder
        
        Args:
            reminder_id (str): ID of the reminder to delete
            
        Returns:
            bool: True if deletion was successful
        """
        response = self.supabase.table('reminders')\
            .delete()\
            .eq('id', reminder_id)\
            .execute()
        return len(response.data) > 0

# Example usage
if __name__ == "__main__":
    # Initialize with your Supabase URL and key
    supabase_url = os.getenv("SUPABASE_URL", "your-supabase-url")
    supabase_key = os.getenv("SUPABASE_KEY", "your-supabase-key")
    
    db = SupabaseManager(supabase_url, supabase_key)
    
    # Example: Create a user profile
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "dob": "1990-01-01",
        "emergency_contact": "123-456-7890",
        "condition": "Migraine",
        "diagnosis_date": "2023-01-01",
        "medications": ["Ibuprofen", "Sumatriptan"]
    }
    
    # Create or update user
    user = db.create_user_profile(user_data)
    print(f"Created/Updated user: {user}")
    
    # Get user profile
    user_profile = db.get_user_profile("test@example.com")
    print(f"User profile: {user_profile}")
    
    # Create a log entry
    log_entry = {
        "date": "2023-10-14",
        "symptoms": ["Headache", "Nausea"],
        "symptom_severity": 7,
        "sleep_quality": "Average",
        "activity_level": "Light",
        "mood": "😐"
    }
    
    created_log = db.create_daily_log("test@example.com", log_entry)
    print(f"Created log: {created_log}")
    
    # Get user logs
    logs = db.get_user_logs("test@example.com", "2023-10-01", "2023-10-15")
    print(f"User logs: {logs}")
    
    # Create a reminder
    reminder = {
        "type": "Medication",
        "date": "2023-10-15",
        "time": "09:00:00",
        "is_recurring": True,
        "recurrence": "daily",
        "text": "Take morning medication"
    }
    
    created_reminder = db.create_reminder("test@example.com", reminder)
    print(f"Created reminder: {created_reminder}")
