import streamlit as st
import authlib
from utils import download_file_from_supabase, upload_file_to_supabase
from datetime import datetime, date
from app_utils import create_supabase_client




IMAGE_ADDRESS = "https://www.shutterstock.com/image-photo/doctor-healthcare-medicine-patient-talking-600nw-2191880035.jpg"
BUCKET_NAME = st.secrets.get("SUPABASE_BUCKET")







def patient_profile_form(patient_id):
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
                    "patient_id": patient_id,
                    "patient_name": name,
                    "dob": dob.isoformat(),
                    "emergency_contact": emergency_contact,
                    "condition": condition,
                    "diagnosis_date": diagnosis_date.isoformat()
                }

                return profile
                # if record_profile_info(client, profile):
                #     st.success("Profile saved successfully!")
                #     return True
                # else:
                #     st.error("Failed to save profile. Please try again.")
                #     return False

               


if not st.user.is_logged_in:
    st.title("Patient Log")
    st.image(IMAGE_ADDRESS)
    if not "profile_login" in st.session_state:
        st.session_state.profile_login = False
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()

else:
    if not "patient_id" in st.session_state:
        st.session_state.patient_id = st.user.sub
    
    if not "profile_exist" in st.session_state:
        st.session_state.profile_exist = False

    client = create_supabase_client()
    if not client:
        st.error("Supabase not configured")
    
    # Check for the record existance
    existing = client.table(st.secrets["SUPABASE_TABLE"]).select("*").eq("patient_id", st.session_state['patient_id']).execute()

    if existing.data:
        st.session_state.profile_exist = True  # means record already exists
        st.success(f"ID: {st.session_state['patient_id']} already exists.")
        # You can optionally merge or update here if needed
        complete = st.button("Complete")
        update = st.button("Update Info")

        if update:
            st.session_state.profile_exist = False
            profile = patient_profile_form(st.session_state["patient_id"])
            
            if profile:
                client.table(st.secrets["SUPABASE_TABLE"]).update(profile).eq("patient_id", st.session_state['patient_id']).execute()
                st.success(f"ID: {st.session_state['patient_id']} updated.")
        if complete:
            st.success("Go to the next page")
    else:
        # Insert new profile
        profile = patient_profile_form(st.session_state["patient_id"])
        try:
            response = client.table(st.secrets["SUPABASE_TABLE"]).insert(profile).execute()

            # Optional: check if Supabase returned data
            if response.data:
                print(f"✅ Successfully inserted record for ID: {st.session_state['patient_id']}")
                
            else:
                print("⚠️ Insert executed but returned no data.")
                

        except Exception as e:
            print(f"❌ Insert failed for ID: {st.session_state['patient_id']} — {e}")
            
        # complete = st.button("Complete")
        # if complete:
        #     st.success("Go to the next page")
        

    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()

    










