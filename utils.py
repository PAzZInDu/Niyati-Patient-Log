import os
from pathlib import Path
from datetime import datetime, date
import json
import pandas as pd
from supabase import create_client, Client
from typing import Optional, Dict, Any, Union


# Common symptoms list
SYMPTOMS = [
    "Headache", "Dizziness", "Nausea", "Fatigue", "Blurred vision",
    "Trouble concentrating", "Trouble sleeping", "Irritability",
    "Sensitivity to light", "Sensitivity to noise", "Memory problems"
]

# Doctor types
DOCTOR_TYPES = [
    "Neurologist", "Physiotherapist", "Psychologist", 
    "General Practitioner", "Other"
]


# Initialize Supabase client
def get_supabase_client(url: str, key: str) -> Client:
    """Initialize and return Supabase client."""
    return create_client(url, key)

def ensure_user_folder(supabase: Client, user_id: str) -> str:
    """Ensure a folder exists for the user in the bucket."""
    # In Supabase Storage, folders are part of the file path
    # So we don't need to create empty folders, just use the path
    return f"{user_id}/"

def upload_file_to_supabase(
    supabase: Client,
    bucket_name: str,
    user_id: str,
    file_name: str,
    file_content: Union[dict, pd.DataFrame],
    content_type: str = "application/json"
) -> bool:
    """
    Upload a file to Supabase Storage.
    
    Args:
        supabase: Supabase client
        bucket_name: Name of the bucket
        user_id: User ID (sub from auth)
        file_name: Name of the file to save
        file_content: Content to save (dict for JSON, DataFrame for CSV)
        content_type: MIME type of the file
    """
    try:
        # Convert content to bytes
        if isinstance(file_content, dict):
            file_data = json.dumps(file_content, indent=2).encode('utf-8')
        elif isinstance(file_content, pd.DataFrame):
            file_data = file_content.to_csv(index=False).encode('utf-8')
        else:
            raise ValueError("Unsupported file_content type. Expected dict or pd.DataFrame")
        
        # Upload file
        file_path = f"{user_id}/{file_name}"
        
        # Check if file exists and update if it does
        try:
            # Try to get the file to check if it exists
            supabase.storage.from_(bucket_name).get_public_url(file_path)
            # If no error, file exists - update it
            result = supabase.storage.from_(bucket_name).update(
                file_path,
                file_data,
                {"content-type": content_type}
            )
        except Exception:
            # If file doesn't exist, create it
            result = supabase.storage.from_(bucket_name).upload(
                file_path,
                file_data,
                {"content-type": content_type}
            )
        
        return True
    except Exception as e:
        print(f"Error uploading file to Supabase: {str(e)}")
        return False

def download_file_from_supabase(
    supabase: Client,
    bucket_name: str,
    user_id: str,
    file_name: str,
    file_type: str = "json"
) -> Union[Dict, pd.DataFrame, None]:
    """
    Download a file from Supabase Storage.
    
    Args:
        supabase: Supabase client
        bucket_name: Name of the bucket
        user_id: User ID (sub from auth)
        file_name: Name of the file to download
        file_type: Type of file ('json' or 'csv')
    """
    try:
        file_path = f"{user_id}/{file_name}"
        
        # Download file
        response = supabase.storage.from_(bucket_name).download(file_path)
        
        if not response:
            return None
            
        # Parse response based on file type
        if file_type.lower() == 'json':
            return json.loads(response.decode('utf-8'))
        elif file_type.lower() == 'csv':
            import io
            return pd.read_csv(io.StringIO(response.decode('utf-8')))
        else:
            return response
            
    except Exception as e:
        print(f"Error downloading file from Supabase: {str(e)}")
        return None

def save_patient_profile(
    supabase: Client,
    bucket_name: str,
    user_id: str,
    profile_data: Dict[str, Any]
) -> bool:
    """Save patient profile to Supabase Storage."""
    return upload_file_to_supabase(
        supabase=supabase,
        bucket_name=bucket_name,
        user_id=user_id,
        file_name="patient_profile.json",
        file_content=profile_data,
        content_type="application/json"
    )

def load_patient_profile(
    supabase: Client,
    bucket_name: str,
    user_id: str
) -> Optional[Dict]:
    """Load patient profile from Supabase Storage."""
    result = download_file_from_supabase(
        supabase=supabase,
        bucket_name=bucket_name,
        user_id=user_id,
        file_name="patient_profile.json",
        file_type="json"
    )
    return result if isinstance(result, dict) else None

def save_daily_log(
    supabase: Client,
    bucket_name: str,
    user_id: str,
    log_data: Dict[str, Any]
) -> bool:
    """
    Save daily log to Supabase Storage.
    If logs.csv exists, append to it. Otherwise, create a new one.
    """
    # Try to load existing logs
    existing_logs = load_daily_logs(supabase, bucket_name, user_id)
    
    # Create a new DataFrame with the new log entry
    new_log = pd.DataFrame([log_data])
    
    if existing_logs is not None and not existing_logs.empty:
        # Append new log to existing logs
        updated_logs = pd.concat([existing_logs, new_log], ignore_index=True)
    else:
        updated_logs = new_log
    
    # Save back to Supabase
    return upload_file_to_supabase(
        supabase=supabase,
        bucket_name=bucket_name,
        user_id=user_id,
        file_name="daily_logs.csv",
        file_content=updated_logs,
        content_type="text/csv"
    )

def load_daily_logs(
    supabase: Client,
    bucket_name: str,
    user_id: str
) -> Optional[pd.DataFrame]:
    """Load daily logs from Supabase Storage."""
    result = download_file_from_supabase(
        supabase=supabase,
        bucket_name=bucket_name,
        user_id=user_id,
        file_name="daily_logs.csv",
        file_type="csv"
    )
    return result if isinstance(result, pd.DataFrame) else None
