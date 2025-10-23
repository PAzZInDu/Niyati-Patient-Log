from embeddings import get_openai_embeddings
import streamlit as st
import pandas as pd
from datetime import date
import numpy as np
import pickle


if not st.user.is_logged_in:
    st.error("Please log in to access the App")
    st.stop()

if not st.session_state.user_profile == True:
    st.error("Please finish setting up the profile")
    st.stop()


MODEL_NAME = "balanced_MLP_best_model"


@st.cache_resource
def load_model(model_name):
    with open(model_name, "rb") as file_name:
        return pickle.load(file_name)

# Load the model
tabular_model = load_model(MODEL_NAME)

# Title
st.title("Soccer Concussion Classification")

#Initialize session state for input fields
for key, default in {"gender": "","issue": "","body_part_affected": ""}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Input fields
#Age
st.session_state.age = st.number_input(
    "Enter Age",
    min_value=3,
    max_value=70,
    value=st.session_state.age,
    key="age_input"
)

#Gender
st.session_state.gender = st.selectbox(
    "Enter The Gender", ("Male", "Female"), 
    index=0 if st.session_state.gender == "Male" else 1
)

#Issue
st.session_state.issue = st.text_input(
    "Issue / Accident Happened", 
    value=st.session_state.issue, 
    placeholder="Eg: Fell Down While Running"
)

#Body part affected
st.session_state.body_part_affected = st.text_input(
    "Body Part Affected", value=st.session_state.body_part_affected
)

# Apply button
if st.button("Apply"):
    if not st.session_state.age or not st.session_state.gender or not st.session_state.issue or not st.session_state.body_part_affected:
        st.error("Please enter all required information")
    else:
        st.success("All information provided!")
        text  = f"{st.session_state.age} Year Old {st.session_state.gender} PLAYING SOCCER, {st.session_state.issue}. Body part affected {st.session_state.body_part_affected}"
        # User Data
        st.subheader("User Data")
        st.divider()
        st.write(text)
        st.divider()
    
        # Generate embeddings
        embeddings = get_openai_embeddings(text)

        # Ensure the embeddings are in 2D shape for the model
        embedding_array = np.array(embeddings).reshape(1, -1)

        # Make prediction
        index = tabular_model.predict(embedding_array)
        labels = ['Concussion', 'No Concussion']
        injury_status = labels[index[0]]

        # Display prediction in Streamlit
        st.subheader("Predictions")
        st.write(f"**{injury_status}**")


# Clear All button (outside Apply block)
if st.button("Clear All"):
    reset_defaults = {
        "gender": "",
        "issue": "",
        "body_part_affected": ""
    }
    for key, default in reset_defaults.items():
        st.session_state[key] = default
    st.rerun()