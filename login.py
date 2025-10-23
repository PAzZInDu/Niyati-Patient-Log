import streamlit as st
import authlib
import time
from datetime import datetime, date, timedelta
from app_utils import create_supabase_client


IMAGE_ADDRESS = "https://www.shutterstock.com/image-photo/doctor-healthcare-medicine-patient-talking-600nw-2191880035.jpg"


def patient_profile_form(patient_id):
    st.title("👤 Patient Profile")
    st.write("Please fill in your basic information.")
    
    with st.form("profile_form"):
        name = st.text_input("Full Name", key="name")
        dob = st.date_input(
            "Date of Birth",
            min_value=date.today() - timedelta(days=365*100),
            max_value=date.today(),
            key="dob"
        )
        emergency_contact = st.text_input("Emergency Contact Number", key="emergency_contact")
        condition = st.text_input("Diagnosed Condition", key="condition")
        diagnosis_date = st.date_input(
            "Date of Diagnosis/Incident",
            max_value=date.today(),
            key="diagnosis_date"
        )
        
        submitted = st.form_submit_button("Save Profile")

        if submitted:
            if not all([name, emergency_contact, condition]):
                st.error("Please fill in all required fields.")
                return None
            if diagnosis_date < dob:
                st.error("Diagnosis date cannot be before date of birth.")
                return None
                
            return {
                "patient_id": patient_id,
                "patient_name": name,
                "dob": dob.isoformat(),
                "emergency_contact": emergency_contact,
                "condition": condition,
                "diagnosis_date": diagnosis_date.isoformat()
            }
    return None

def main():
    if not st.user.is_logged_in:
        st.title("Patient Log")
        st.image(IMAGE_ADDRESS)
        if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
            st.login()
        return

    # Initialize session state
    if "patient_id" not in st.session_state:
        st.session_state.patient_id = st.user.sub

    # Initialize Supabase client
    try:
        client = create_supabase_client()
        if not client:
            st.error("Failed to initialize database connection.")
            return

        # Check for existing record
        response = client.table(st.secrets["supabase"]["SUPABASE_TABLE"])\
                       .select("*")\
                       .eq("patient_id", st.session_state.patient_id)\
                       .execute()

        if response.data:
            st.subheader(f"Welcome {st.user.name}")
            st.info("Proceed to Daily Log")
        else:
            # Show profile form for new users
            new_profile = patient_profile_form(st.session_state.patient_id)
            if new_profile:
                try:
                    response = client.table(st.secrets["supabase"]["SUPABASE_TABLE"])\
                                   .insert(new_profile)\
                                   .execute()

                    if response.data:
                        st.success("Profile saved successfully!")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Failed to save profile. Please try again.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()

if __name__ == "__main__":
    main()