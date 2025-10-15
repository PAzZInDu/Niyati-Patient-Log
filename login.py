import streamlit as st
import authlib

#from app import chat

IMAGE_ADDRESS = "https://natureconservancy-h.assetsadobe.com/is/image/content/dam/tnc/nature/en/photos/s/h/shutterstock_1512536354.jpg?crop=0%2C317%2C2664%2C1465&wid=1300&hei=715&scl=2.0492307692307694"
# title
#st.title("Google Login App")

#st.image(IMAGE_ADDRESS)
#if not st.experimental_user.is_logged_in:

if not st.user.is_logged_in:
    st.title("Butterfly Classification")
    st.image(IMAGE_ADDRESS)
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()

else:
    st.success("Please open the app")
    #st.html(f"Hello, <span style='color: orange; font-weight: bold;'>{st.experimental_user.name}</span>!")
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()
    #chat()

    