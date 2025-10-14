import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
import os
from pathlib import Path
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from upload import SupabaseManager


# # Initialize Supabase
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SUPABASE_URL = "https://bxihryeeefwyomrwbiwe.supabase.co"
SUPABASE_KEY = "sb_secret_O2aviL26RVKq2QSW2DdQ6g_Q7eAqEYL"



def get_db():
    """Get Supabase client"""
    if 'db' not in st.session_state:
        st.session_state.db = SupabaseManager(SUPABASE_URL, SUPABASE_KEY)
    return st.session_state.db

# Page configuration
st.set_page_config(
    page_title="Patient Health Tracker",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'daily_log'

# Initialize session state for user data
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'daily_logs' not in st.session_state:
    st.session_state.daily_logs = []

# Data storage functions
def save_user_data():
    """Save user data to Supabase"""
    if 'user' in st.session_state and st.session_state.user_data:
        db = get_db()
        user_data = st.session_state.user_data.copy()
        user_data['email'] = st.session_state.user['email']
        db.create_user_profile(user_data)

def load_user_data():
    """Load user data from Supabase"""
    if 'user' in st.session_state:
        db = get_db()
        user_data = db.get_user_profile(st.session_state.user['email'])
        if user_data:
            # Remove internal fields
            user_data.pop('created_at', None)
            user_data.pop('updated_at', None)
            user_data.pop('id', None)
            user_data.pop('email', None)
            st.session_state.user_data = user_data
        else:
            st.session_state.user_data = {}

def save_daily_log():
    """Save daily log entry to Supabase"""
    if 'current_log' in st.session_state and 'user' in st.session_state:
        db = get_db()
        log_data = st.session_state.current_log.copy()
        db.create_daily_log(st.session_state.user['email'], log_data)
        # Refresh logs after saving
        load_daily_logs()

def load_daily_logs():
    """Load daily logs from Supabase"""
    if 'user' in st.session_state:
        db = get_db()
        # Load logs for the last 30 days by default
        start_date = (date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        logs = db.get_user_logs(st.session_state.user['email'], start_date=start_date)
        st.session_state.daily_logs = logs
        return logs
    return []

# Navigation
def navigation():
    st.sidebar.title("🏥 Patient Health Tracker")
    st.sidebar.write("---")
    
    # User info (from Google OAuth)
    if 'user' in st.session_state:
        st.sidebar.write(f"👤 {st.session_state.user.get('name', 'User')}")
        st.sidebar.write(f"📧 {st.session_state.user.get('email', '')}")
        st.sidebar.write("---")
    
    # Menu
    menu = {
        "📝 Daily Log": "daily_log",
        "👤 Profile": "profile",
        "📊 Reports": "reports",
        "🔔 Reminders": "reminders",
        "⚙️ Settings": "settings"
    }
    
    for item, page in menu.items():
        if st.sidebar.button(item, key=page, use_container_width=True):
            st.session_state.page = page
    
    st.sidebar.write("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        # Here you would add your logout logic
        st.session_state.clear()
        st.rerun()

# Profile Page
def profile_page():
    st.title("👤 Patient Profile")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Personal Information")
            name = st.text_input("Full Name", value=st.session_state.user_data.get('name', ''))
            dob = st.date_input("Date of Birth", 
                              value=pd.to_datetime(st.session_state.user_data.get('dob', '2000-01-01')) if 'dob' in st.session_state.user_data else None,
                              max_value=date.today())
            emergency_contact = st.text_input("Emergency Contact", 
                                           value=st.session_state.user_data.get('emergency_contact', ''))
            
        with col2:
            st.subheader("Medical Information")
            condition = st.text_input("Diagnosed Condition", 
                                    value=st.session_state.user_data.get('condition', ''))
            diagnosis_date = st.date_input("Date of Diagnosis",
                                         value=pd.to_datetime(st.session_state.user_data.get('diagnosis_date', date.today())) if 'diagnosis_date' in st.session_state.user_data else None,
                                         max_value=date.today())
            medications = st.text_area("Current Medications (one per line)", 
                                     value="\n".join(st.session_state.user_data.get('medications', [])))
        
        if st.form_submit_button("Save Profile"):
            st.session_state.user_data = {
                'name': name,
                'dob': dob.strftime('%Y-%m-%d'),
                'emergency_contact': emergency_contact,
                'condition': condition,
                'diagnosis_date': diagnosis_date.strftime('%Y-%m-%d'),
                'medications': [m.strip() for m in medications.split('\n') if m.strip()]
            }
            save_user_data()
            st.success("Profile saved successfully!")

# Daily Log Page
def daily_log_page():
    st.title("📝 Daily Log Entry")
    
    with st.form("daily_log_form"):
        # Date and Time
        col1, col2 = st.columns(2)
        with col1:
            log_date = st.date_input("Date", value=date.today())
        with col2:
            log_time = st.time_input("Time", value=datetime.now().time())
        
        # Symptoms
        st.subheader("😵‍💫 Symptoms")
        symptoms = [
            "Headache", "Dizziness", "Nausea", "Fatigue", "Blurred vision",
            "Trouble concentrating", "Trouble sleeping", "Irritability",
            "Sensitivity to light", "Sensitivity to noise", "Memory problems"
        ]
        
        selected_symptoms = []
        cols = st.columns(3)
        for i, symptom in enumerate(symptoms):
            with cols[i % 3]:
                if st.checkbox(symptom, key=f"symptom_{symptom}"):
                    selected_symptoms.append(symptom)
        
        other_symptom = st.text_input("Other symptoms (please specify)")
        if other_symptom:
            selected_symptoms.append(f"Other: {other_symptom}")
        
        # Medication
        st.subheader("💊 Medication")
        med_taken = st.radio("Have you taken your prescribed medication today?", 
                            ["Yes", "No"], 
                            index=1 if not st.session_state.user_data.get('medications') else 0)
        
        medication_details = ""
        if med_taken == "Yes" and st.session_state.user_data.get('medications'):
            medication = st.selectbox("Which medication?", 
                                    [""] + st.session_state.user_data.get('medications', []))
            if medication:
                medication_details = st.text_area("Dosage and time taken")
        
        # Doctor/Treatment
        st.subheader("👨‍⚕️ Doctor / Treatment")
        doctor_visit = st.radio("Did you visit a doctor today?", ["Yes", "No"], index=1)
        
        doctor_details = {}
        if doctor_visit == "Yes":
            doctor_type = st.selectbox("What kind of doctor?", 
                                     ["", "Neurologist", "Physiotherapist", 
                                      "Psychologist", "General Practitioner", "Other"])
            if doctor_type:
                advice = st.text_area("Any new advice or change in medication?")
                doctor_details = {
                    "type": doctor_type,
                    "advice": advice
                }
        
        # Recovery Indicators
        st.subheader("🧩 Recovery Indicators")
        symptom_severity = st.slider("How severe are your symptoms today? (1-10)", 1, 10, 5)
        sleep_quality = st.radio("How was your sleep last night?", 
                                ["😊 Good", "😐 Average", "😞 Poor"])
        activity_level = st.radio("Did you do any physical activity today?",
                                 ["None", "Light", "Moderate", "Intense"])
        mood = st.radio("Overall feeling:", 
                       ["😀", "😊", "😐", "😞", "😢"])
        
        # Submit button
        if st.form_submit_button("Save Daily Log"):
            log_entry = {
                "date": log_date.strftime('%Y-%m-%d'),
                "time": str(log_time),
                "symptoms": selected_symptoms,
                "medication_taken": med_taken == "Yes",
                "medication_details": medication_details if med_taken == "Yes" else "",
                "doctor_visit": doctor_visit == "Yes",
                "doctor_details": doctor_details if doctor_visit == "Yes" else {},
                "symptom_severity": symptom_severity,
                "sleep_quality": sleep_quality,
                "activity_level": activity_level,
                "mood": mood,
                "timestamp": datetime.now().isoformat()
            }
            
            st.session_state.current_log = log_entry
            save_daily_log()
            st.success("Daily log saved successfully!")

# Reports Page
def reports_page():
    st.title("📊 Reports & History")
    
    if not st.session_state.daily_logs:
        st.info("No logs available yet. Start by adding daily logs.")
        return
    
    # Load logs
    logs_df = pd.DataFrame(st.session_state.daily_logs)
    logs_df['date'] = pd.to_datetime(logs_df['date'])
    
    # Date range selector
    min_date = logs_df['date'].min().date()
    max_date = logs_df['date'].max().date()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    
    # Filter logs by date range
    filtered_logs = logs_df[(logs_df['date'].dt.date >= start_date) & 
                           (logs_df['date'].dt.date <= end_date)]
    
    if filtered_logs.empty:
        st.warning("No logs found in the selected date range.")
        return
    
    # Display summary statistics
    st.subheader("📈 Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Logs", len(filtered_logs))
    with col2:
        avg_severity = filtered_logs['symptom_severity'].mean()
        st.metric("Average Symptom Severity", f"{avg_severity:.1f}/10")
    with col3:
        most_common_symptom = "N/A"
        if not filtered_logs['symptoms'].empty:
            all_symptoms = [symptom for sublist in filtered_logs['symptoms'] for symptom in sublist]
            if all_symptoms:
                most_common_symptom = max(set(all_symptoms), key=all_symptoms.count)
        st.metric("Most Common Symptom", most_common_symptom)
    
    # Symptom trend chart
    st.subheader("📊 Symptom Severity Over Time")
    if not filtered_logs.empty:
        chart_data = filtered_logs[['date', 'symptom_severity']].set_index('date')
        st.line_chart(chart_data)
    
    # Sleep quality distribution
    st.subheader("😴 Sleep Quality Distribution")
    if not filtered_logs.empty and 'sleep_quality' in filtered_logs.columns:
        sleep_data = filtered_logs['sleep_quality'].value_counts()
        st.bar_chart(sleep_data)
    
    # Data table
    st.subheader("📋 Log Entries")
    display_cols = ['date', 'symptom_severity', 'sleep_quality', 'activity_level', 'mood']
    st.dataframe(filtered_logs[display_cols], use_container_width=True)
    
    # Export options
    st.download_button(
        label="📥 Export to CSV",
        data=filtered_logs.to_csv(index=False).encode('utf-8'),
        file_name=f"health_logs_{start_date}_to_{end_date}.csv",
        mime='text/csv',
    )

# Reminders Page
def load_reminders():
    """Load reminders from Supabase"""
    if 'user' in st.session_state:
        db = get_db()
        st.session_state.reminders = db.get_user_reminders(st.session_state.user['email'])
    else:
        st.session_state.reminders = []

def save_reminder(reminder_data):
    """Save a reminder to Supabase"""
    if 'user' in st.session_state:
        db = get_db()
        return db.create_reminder(st.session_state.user['email'], reminder_data)
    return None

def update_reminder(reminder_id, updates):
    """Update a reminder in Supabase"""
    db = get_db()
    return db.update_reminder(reminder_id, updates)

def delete_reminder(reminder_id):
    """Delete a reminder from Supabase"""
    db = get_db()
    return db.delete_reminder(reminder_id)

def reminders_page():
    st.title("🔔 Reminders")
    
    # Load reminders if not in session state
    if 'reminders' not in st.session_state:
        load_reminders()
    
    # Add new reminder
    with st.form("add_reminder"):
        st.subheader("Add New Reminder")
        
        col1, col2 = st.columns(2)
        with col1:
            reminder_type = st.selectbox("Reminder Type", 
                                       ["Medication", "Appointment", "Log Entry", "Other"])
            reminder_time = st.time_input("Time")
        with col2:
            reminder_date = st.date_input("Date", min_value=date.today())
            is_recurring = st.checkbox("Recurring")
            
        reminder_text = st.text_area("Reminder Details")
        
        if st.form_submit_button("Add Reminder"):
            new_reminder = {
                "id": len(st.session_state.reminders) + 1,
                "type": reminder_type,
                "date": reminder_date.strftime('%Y-%m-%d'),
                "time": str(reminder_time),
                "is_recurring": is_recurring,
                "text": reminder_text,
                "is_completed": False
            }
            saved_reminder = save_reminder(new_reminder)
            if saved_reminder:
                load_reminders()  # Refresh the list
                st.success("Reminder added!")
            else:
                st.error("Failed to save reminder.")
    
    # Display reminders
    st.subheader("Upcoming Reminders")
    if not st.session_state.reminders:
        st.info("No reminders set up yet.")
    else:
        for reminder in st.session_state.reminders:
            with st.container():
                col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
                with col1:
                    st.markdown(f"**{reminder['type']}** - {reminder['date']} at {reminder['time']}")
                    st.caption(reminder['text'])
                    if reminder['is_recurring']:
                        st.caption("🔄 Recurring")
                with col2:
                    if st.button("✓", key=f"complete_{reminder['id']}"):
                        if update_reminder(reminder['id'], {"is_completed": True, "completed_at": datetime.utcnow().isoformat()}):
                            load_reminders()  # Refresh the list
                            st.rerun()
                        else:
                            st.error("Failed to mark reminder as complete.")
                with col3:
                    if st.button("✕", key=f"delete_{reminder['id']}"):
                        if delete_reminder(reminder['id']):
                            load_reminders()  # Refresh the list
                            st.rerun()
                        else:
                            st.error("Failed to delete reminder.")
                st.write("---")

# Settings Page
def settings_page():
    st.title("⚙️ Settings")
    
    st.subheader("Account Settings")
    with st.form("account_settings"):
        # Theme selection
        theme = st.selectbox("Theme", ["Light", "Dark", "System"])
        
        # Notification preferences
        st.subheader("Notification Preferences")
        email_notifications = st.checkbox("Email Notifications", value=True)
        push_notifications = st.checkbox("Push Notifications", value=True)
        
        # Data export
        st.subheader("Data Management")
        if st.form_submit_button("Export All Data"):
            # In a real app, you would implement data export functionality here
            st.success("Data export started. You'll receive an email when it's ready.")
        
        if st.form_submit_button("Save Settings"):
            # Save settings to session state or database
            st.session_state.settings = {
                "theme": theme,
                "email_notifications": email_notifications,
                "push_notifications": push_notifications
            }
            st.success("Settings saved successfully!")
    
    st.subheader("Danger Zone")
    with st.expander("Delete Account"):
        st.warning("This action cannot be undone. All your data will be permanently deleted.")
        if st.button("Delete My Account", type="primary"):
            # In a real app, you would implement account deletion logic here
            st.error("Account deletion is not implemented in this demo.")

# Main App
def main():
    # Load data
    load_user_data()
    st.session_state.daily_logs = load_daily_logs()
    
    # Navigation
    navigation()
    
    # Page routing
    if st.session_state.page == 'profile':
        profile_page()
    elif st.session_state.page == 'reports':
        reports_page()
    elif st.session_state.page == 'reminders':
        reminders_page()
    elif st.session_state.page == 'settings':
        settings_page()
    else:  # Default to daily log
        daily_log_page()

if __name__ == "__main__":
    # Check if Supabase credentials are set
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Error: SUPABASE_URL and SUPABASE_KEY must be set in the .env file")
        st.stop()
    
    # For demo purposes, we'll simulate a logged-in user
    if 'user' not in st.session_state:
        st.session_state.user = {
            'name': 'John Doe',
            'email': os.getenv("DEMO_EMAIL", "john.doe@example.com")
        }
    
    # Initialize user data if not exists
    load_user_data()
    if not st.session_state.get('user_data'):
        st.session_state.user_data = {
            'name': 'John Doe',
            'dob': '1985-07-15',
            'emergency_contact': 'Jane Doe (Spouse) - 555-123-4567',
            'condition': 'Migraine',
            'diagnosis_date': '2023-01-15',
            'medications': ['Sumatriptan 50mg', 'Propranolol 40mg']
        }
    
    main()
