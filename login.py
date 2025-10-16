import streamlit as st
import authlib
from supabase import Client, create_client
from utils import download_file_from_supabase
from datetime import datetime, date


IMAGE_ADDRESS = "https://www.shutterstock.com/image-photo/doctor-healthcare-medicine-patient-talking-600nw-2191880035.jpg"
BUCKET_NAME = st.secrets.get("SUPABASE_BUCKET")


def save_patient_profile(profile, user_id):
    
    success = save_profile_to_supabase(client, BUCKET_NAME, user_id, profile)
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
                    "last_updated":  datetime.now().isoformat()
                    
                }
                if save_patient_profile(profile, user_id):
                    st.success("Profile saved successfully!")
                else:
                    st.error("Failed to save profile. Please try again.")









if not st.user.is_logged_in:
    st.title("Patient Log")
    st.image(IMAGE_ADDRESS)
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()

else:
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()


client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
if not client:
    st.error("Unable to save profile: Supabase not configured")
    

# st.session_state.user_id = st.user.sub 


result = download_file_from_supabase(
    supabase=client,
    bucket_name=BUCKET_NAME,
    user_id=44215457,
    file_name="patient_profile.json",
    file_type="json"
)

if result is None:
    patient_profile_form()
else:
    st.success("Thank you")



