import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import uuid


from app_utils import create_supabase_client

# Import shared variables and functions from 00_User_Info
# from pages.User_Info import (
#     supabase, BUCKET_NAME, SYMPTOMS, DOCTOR_TYPES,
#     get_user_id, load_patient_profile
# )

if not st.user.is_logged_in:
    st.error("Please log in to access the App")
    st.stop()


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

mood_mapping = {
    "😀": 5,
    "🙂": 4,
    "😐": 3,
    "🙁": 2,
    "😢": 1
}

# App
st.title("📝 Daily Log Entry")

# Load profile to get user's name
# profile = load_patient_profile()
# if not profile:
#     st.error("Please complete your profile first.")
    
    
st.write(f"Welcome! Let's log your day.")



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
    
    mood_choice = st.radio(
        "Overall feeling today:",
        list(mood_mapping.keys()),
        horizontal=True
    )
    
    submitted = st.form_submit_button("Save Daily Log")

    if submitted:
        log_entry = {
            'token': str(uuid.uuid4()),
            'patient_id': st.session_state['patient_id'],
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
            'mood': mood_mapping[mood_choice],
            'logged_at': datetime.utcnow().isoformat()
        }

        client = create_supabase_client()

        client.table(st.secrets["User_data_log"]).insert(log_entry).execute()
        st.success("Your Information is submitted")









        
        
        