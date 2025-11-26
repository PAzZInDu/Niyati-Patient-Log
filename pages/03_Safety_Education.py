import streamlit as st
from quiz import show_quiz
from med_instructions import concussion_instructions


def safety_tab():
    show_quiz()

def health_tab():
    concussion_instructions()



def main():
    st.title("🏥 Safety & Health Hub")
    st.write("Explore our comprehensive resources for player safety and health management.")
    
    tab1, tab2 = st.tabs(["🏗️ Take Safety Quiz", "❤️ Health"])
    
    with tab1:
        safety_tab()
    
    with tab2:
        health_tab()
    

if __name__ == "__main__":
    main()