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

# Supabase configuration (replace with your actual values)
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
BUCKET_NAME = "SUPABUCKET"  # Your bucket name

# Initialize Supabase client
@st.cache_resource
def get_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Supabase credentials not configured. Please set SUPABASE_URL and SUPABASE_KEY in secrets.toml")
        return None
    return get_supabase_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

def get_user_id():
    # This is a placeholder. In a real app, you'd get this from your auth system
    if 'user_id' not in st.session_state:
        # For demo purposes, we'll use a default user ID
        st.session_state.user_id = "demo_user_" + str(hash(st.experimental_user.email) if hasattr(st, 'experimental_user') and st.experimental_user else 123)
    return st.session_state.user_id

# Page config
st.set_page_config(
    page_title="Patient Recovery Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

def load_daily_logs():
    if not supabase:
        return pd.DataFrame(columns=[
            'date', 'time', 'symptoms', 'other_symptoms', 'medication_taken',
            'medication_name', 'doctor_visited', 'doctor_type', 'doctor_notes',
            'symptom_severity', 'sleep_quality', 'physical_activity', 'mood'
        ])
    
    user_id = get_user_id()
    logs = load_logs_from_supabase(supabase, BUCKET_NAME, user_id)
    
    if logs is None or logs.empty:
        return pd.DataFrame(columns=[
            'date', 'time', 'symptoms', 'other_symptoms', 'medication_taken',
            'medication_name', 'doctor_visited', 'doctor_type', 'doctor_notes',
            'symptom_severity', 'sleep_quality', 'physical_activity', 'mood'
        ])
    
    # Ensure date is in datetime format
    if 'date' in logs.columns:
        logs['date'] = pd.to_datetime(logs['date'], errors='coerce')
    return logs

def save_daily_log(log_entry):
    if not supabase:
        st.error("Unable to save log: Supabase not configured")
        return False
    
    user_id = get_user_id()
    return save_log_to_supabase(supabase, BUCKET_NAME, user_id, log_entry)

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

def daily_log_form():
    st.title("📝 Daily Log Entry")
    st.write(f"Welcome back, {st.session_state.profile['name']}! Let's log your day.")
    
    with st.form("daily_log_form"):
        # Date and Time
        col1, col2 = st.columns(2)
        with col1:
            log_date = st.date_input("Date", value=date.today())
        with col2:
            log_time = st.time_input("Time", value=datetime.now().time())
        
        # Symptoms
        st.subheader("😵‍💫 Symptoms")
        selected_symptoms = st.multiselect(
            "What kind of problems are you experiencing today?",
            SYMPTOMS
        )
        other_symptoms = st.text_input("Other symptoms (please specify)")
        
        # Medication
        st.subheader("💊 Medication")
        med_taken = st.radio(
            "Have you taken your prescribed medication today?",
            ["Yes", "No"],
            horizontal=True
        )
        
        medication_name = ""
        if med_taken == "Yes":
            if st.session_state.profile.get('medications'):
                medication_name = st.selectbox(
                    "Which medication?",
                    st.session_state.profile['medications']
                )
            else:
                medication_name = st.text_input("Enter medication name")
        
        # Doctor Visit
        st.subheader("👨‍⚕️ Doctor / Treatment")
        doctor_visited = st.radio(
            "Did you visit a doctor today?",
            ["Yes", "No"],
            horizontal=True
        )
        
        doctor_type = ""
        doctor_notes = ""
        if doctor_visited == "Yes":
            doctor_type = st.selectbox("What kind of doctor?", DOCTOR_TYPES)
            if doctor_type == "Other":
                doctor_type = st.text_input("Please specify")
            doctor_notes = st.text_area("Any new advice or change in medication?")
        
        # Recovery Indicators
        st.subheader("🧩 Recovery Indicators")
        symptom_severity = st.slider(
            "How severe are your symptoms today?",
            1, 10, 5,
            help="1 = Very mild, 10 = Extremely severe"
        )
        
        sleep_quality = st.radio(
            "How was your sleep last night?",
            ["😊 Good", "😐 Average", "😞 Poor"],
            horizontal=True
        )
        
        physical_activity = st.radio(
            "Did you do any physical activity today?",
            ["🚶‍♂️ Light", "🏃‍♂️ Moderate", "💪 Intense", "❌ None"],
            horizontal=True
        )
        
        mood = st.radio(
            "Overall feeling today:",
            ["😀", "🙂", "😐", "🙁", "😢"],
            horizontal=True
        )
        
        submitted = st.form_submit_button("Save Daily Log")
        if submitted:
            log_entry = {
                'date': log_date.isoformat(),
                'time': log_time.strftime("%H:%M"),
                'symptoms': ", ".join(selected_symptoms),
                'other_symptoms': other_symptoms,
                'medication_taken': med_taken == "Yes",
                'medication_name': medication_name if med_taken == "Yes" else "",
                'doctor_visited': doctor_visited == "Yes",
                'doctor_type': doctor_type if doctor_visited == "Yes" else "",
                'doctor_notes': doctor_notes if doctor_visited == "Yes" else "",
                'symptom_severity': symptom_severity,
                'sleep_quality': sleep_quality.split()[0],
                'physical_activity': physical_activity.split()[-1],
                'mood': mood,
                'logged_at': datetime.utcnow().isoformat()
            }
            
            if save_daily_log(log_entry):
                st.success("Daily log saved successfully!")
            else:
                st.error("Failed to save daily log. Please try again.")

def dashboard():
    st.title("📊 Recovery Dashboard")
    
    if not LOGS_FILE.exists():
        st.info("No logs available yet. Please complete a daily log entry first.")
        return
    
    logs = load_daily_logs()
    
    if logs.empty:
        st.info("No logs available yet. Please complete a daily log entry first.")
        return
    
    # Ensure date column is in datetime format
    logs['date'] = pd.to_datetime(logs['date'], format='%Y-%m-%d', errors='coerce')
    # Remove any rows with invalid dates
    logs = logs.dropna(subset=['date'])
    
    # Summary stats
    st.subheader("Recovery Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Days Logged", len(logs))
    with col2:
        avg_severity = logs['symptom_severity'].mean().round(1)
        st.metric("Average Symptom Severity", f"{avg_severity}/10")
    with col3:
        last_mood = logs.iloc[-1]['mood']
        st.metric("Most Recent Mood", last_mood)
    
    # Symptom severity over time
    st.subheader("Symptom Severity Over Time")
    st.line_chart(data=logs, x='date', y='symptom_severity')
    
    # Symptoms frequency
    st.subheader("Most Common Symptoms")
    symptom_counts = {}
    for symptoms in logs['symptoms']:
        for symptom in [s.strip() for s in symptoms.split(',') if s.strip()]:
            symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
    
    if symptom_counts:
        st.bar_chart(pd.DataFrame({
            'Symptom': list(symptom_counts.keys()),
            'Count': list(symptom_counts.values())
        }).set_index('Symptom'))
    
    # Show recent logs
    st.subheader("Recent Logs")
    st.dataframe(
        logs.sort_values('date', ascending=False).head(10),
        column_config={
            'date': "Date",
            'symptom_severity': st.column_config.NumberColumn("Severity (1-10)", format="%d")
        },
        hide_index=True
    )

def main():
    # Sidebar navigation
    st.sidebar.title("Patient Recovery Tracker")
    
    if not st.session_state.profile_exists:
        patient_profile_form()
        return
    
    # Load profile if not already loaded
    if 'profile' not in st.session_state:
        st.session_state.profile = load_patient_profile()
    
    # Navigation
    page = st.sidebar.radio(
        "Go to",
        ["📝 Daily Log", "📊 Dashboard", "👤 Profile"]
    )
    
    if page == "📝 Daily Log":
        daily_log_form()
    elif page == "📊 Dashboard":
        dashboard()
    elif page == "👤 Profile":
        patient_profile_form()
    
    # Add some info in the sidebar
    st.sidebar.divider()
    st.sidebar.info(
        "ℹ️ This app helps you track your recovery progress. "
        "Log your symptoms, medications, and doctor visits daily for best results."
    )

if __name__ == "__main__":
    main()
