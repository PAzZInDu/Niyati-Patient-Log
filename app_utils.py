# app_utils.py
import streamlit as st
from supabase import Client, create_client


def create_supabase_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
