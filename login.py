import streamlit as st
import authlib
from supabase import Client, create_client


IMAGE_ADDRESS = "https://www.shutterstock.com/image-photo/doctor-healthcare-medicine-patient-talking-600nw-2191880035.jpg"

def save_patient_profile(profile, user_id):
    
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
                    "last_updated":  datetime.now().isoformat()
                    
                }
                if save_patient_profile(profile):
                    st.success("Profile saved successfully!")
                    st.rerun()
                else:
                    st.error("Failed to save profile. Please try again.")


# def google_log_in():
#     if not st.user.is_logged_in:
#         st.title("Patient Log")
#         st.image(IMAGE_ADDRESS)
#         if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
#             st.login()

#     else:
#         st.success("Please open the app")
#         if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
#             st.logout()




def main():

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
        return False

    user_id = st.user.sub


if __name__ == "__main__":
    main()