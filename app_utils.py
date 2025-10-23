# app_utils.py
import streamlit as st
from datetime import date
from supabase import Client, create_client


def create_supabase_client():
    return create_client(st.secrets["supabase"]["SUPABASE_URL"], st.secrets["supabase"]["SUPABASE_KEY"])



def calculate_age(dob_str):
   dob_obj = date.fromisoformat(dob_str)
   today = date.today()
   age = today.year - dob_obj.year - ((today.month, today.day) < (dob_obj.month, dob_obj.day))
   return age