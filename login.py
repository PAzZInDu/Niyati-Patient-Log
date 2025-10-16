import streamlit as st
import authlib
from supabase import Client, create_client
from utils import download_file_from_supabase, upload_file_to_supabase
from datetime import datetime, date


IMAGE_ADDRESS = "https://www.shutterstock.com/image-photo/doctor-healthcare-medicine-patient-talking-600nw-2191880035.jpg"
BUCKET_NAME = st.secrets.get("SUPABASE_BUCKET")




def record_profile_info(client: Client, profile: dict) -> bool:
    # Map profile keys to your table columns
    payload = {
        "patient_id": profile.get("patient_id"),
        "patient_name": profile.get("name"),
        "dob": profile.get("dob"),
        "contact_num": profile.get("emergency_contact"),
        "diagnosis": profile.get("condition"),
        "date_of_diagnosis": profile.get("diagnosis_date")
    }
    try:
        response = client.table("ProfileData").insert(payload).execute()
    except Exception as exc:
        print(f"Storing logo metadata failed: {exc}")
        return False

    error = getattr(response, "error", None)
    if error:
        message = getattr(error, "message", str(error))
        print(f"Storing logo metadata failed: {message}")
        return False

    return True



def patient_profile_form():
    st.title("👤 Patient Profile")
    st.write("Please fill in your basic information.")
    
    with st.form("profile_form"):
        id = st.text_input("Enter Your ID")
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
                    "patient_id": id,
                    "name": name,
                    "dob": dob.isoformat(),
                    "emergency_contact": emergency_contact,
                    "condition": condition,
                    "diagnosis_date": diagnosis_date.isoformat(),
                    "medications": [],
                    "last_updated":  datetime.now().isoformat()
                    
                }


                if record_profile_info(client, profile):
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
    



patient_profile_form()




