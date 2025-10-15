import streamlit as st
import authlib

#from app import chat

IMAGE_ADDRESS = "https://www.shutterstock.com/image-photo/doctor-healthcare-medicine-patient-talking-600nw-2191880035.jpg"
#st.title("Google Login App")

#st.image(IMAGE_ADDRESS)
#if not st.experimental_user.is_logged_in:

if not st.user.is_logged_in:
    st.title("Patient Log")
    st.image(IMAGE_ADDRESS)
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()

else:
    st.success("Please open the app")
    #st.html(f"Hello, <span style='color: orange; font-weight: bold;'>{st.experimental_user.name}</span>!")
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()
    #chat()

    