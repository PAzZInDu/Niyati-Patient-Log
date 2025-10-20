import streamlit as st
import authlib
from datetime import datetime, date, timedelta
from app_utils import create_supabase_client


IMAGE_ADDRESS = "https://www.shutterstock.com/image-photo/doctor-healthcare-medicine-patient-talking-600nw-2191880035.jpg"


def patient_profile_form(patient_id):
    st.title("👤 Patient Profile")
    st.write("Please fill in your basic information.")
    
    with st.form("profile_form"):
        name = st.text_input("Full Name")
        dob = st.date_input("Date of Birth", min_value=(date.today() - timedelta(days=365*100)),max_value=date.today())
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




# App Login
if not st.user.is_logged_in:
    st.title("Patient Log")
    st.image(IMAGE_ADDRESS)
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()

else:
    if not "patient_id" in st.session_state:
        st.session_state.patient_id = st.user.sub

    client = create_supabase_client()
    if not client:
        st.error("Supabase not configured")
    
    # Check for the record existance
    existing = client.table(st.secrets["SUPABASE_TABLE"]).select("*").eq("patient_id", st.session_state['patient_id']).execute()

    if existing.data:
        st.subheader(f"Welcome {st.user.name}")
        st.info("Proceed to Daily Log")

        
    else:
        # Insert new profile
        new_profile = patient_profile_form(st.session_state["patient_id"])
        try:
            response = client.table(st.secrets["SUPABASE_TABLE"]).insert(new_profile).execute()

            # Optional: check if Supabase returned data
            if response.data:
                st.toast("Successfully inserted record for ID", icon="✅")
                #print(f"✅ Successfully inserted record for ID: {st.session_state['patient_id']}")
                st.rerun()

                
            else:
                print("⚠️ Insert executed but returned no data.")
                

        except Exception as e:
            print(f"❌ Insert failed for ID: {st.session_state['patient_id']} — {e}")
            

    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()

    










