import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import json
import os
from pathlib import Path
from data import (
    get_supabase_client,
    save_patient_profile as save_profile_to_supabase,
    load_patient_profile as load_profile_from_supabase,
    save_daily_log as save_log_to_supabase,
    load_daily_logs as load_logs_from_supabase
)



# Supabase configuration
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
BUCKET_NAME = st.secrets.get("BUCKET_NAME")

# Initialize Supabase client
@st.cache_resource
def get_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Supabase credentials not configured. Please set SUPABASE_URL and SUPABASE_KEY in secrets.toml")
        return None
    return get_supabase_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

def get_user_id():
    """Return a persistent unique user ID based on Google OAuth login."""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = st.user.sub
    return st.session_state.user_id

# Initialize session state
if 'profile_exists' not in st.session_state:
    if supabase:
        user_id = get_user_id()
        profile = load_profile_from_supabase(supabase, BUCKET_NAME, user_id)
        st.session_state.profile_exists = profile is not None
    else:
        st.session_state.profile_exists = False

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

def load_patient_profile():
    if not supabase:
        return None
    user_id = get_user_id()
    return load_profile_from_supabase(supabase, BUCKET_NAME, user_id)

def save_patient_profile(profile):
    if not supabase:
        st.error("Unable to save profile: Supabase not configured")
        return False
    user_id = get_user_id()
    success = save_profile_to_supabase(supabase, BUCKET_NAME, user_id, profile)
    if success:
        st.session_state.profile_exists = True
    return success

def patient_profile_form():
    st.title("👤 Patient Profile")
    st.write("Please fill in your basic information.")
    
    with st.form("profile_form"):
        name = st.text_input("Full Name")
        dob = st.date_input("Date of Birth", max_value=date.today())
        emergency_contact = st.text_input("Emergency Contact Number")
        condition = st.text_input("Diagnosed Condition")
        diagnosis_date = st.date_input("Date of Diagnosis/Incident", max_value=date.today())
        
        submitted = st.form_submit_button("Save Profile")
        if submitted:
            if not all([name, emergency_contact, condition]):
                st.error("Please fill in all required fields.")
            else:
                profile = {
                    "name": name,
                    "dob": dob.isoformat(),
                    "emergency_contact": emergency_contact,
                    "condition": condition,
                    "diagnosis_date": diagnosis_date.isoformat(),
                    "medications": [],
                    "last_updated": datetime.utcnow().isoformat()
                }
                if save_patient_profile(profile):
                    st.success("Profile saved successfully!")
                    st.rerun()
                else:
                    st.error("Failed to save profile. Please try again.")

# Main function
if not st.session_state.profile_exists:
    patient_profile_form()
else:
    st.session_state.profile = load_patient_profile()
    st.info("Profile already exists. You can view or update it from the Profile page.")
