import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app_utils import create_supabase_client



if not st.user.is_logged_in:
    st.error("Please log in to access the App")
    st.stop()


st.title("📊 Recovery Dashboard")


# Load logs
client = create_supabase_client()
log_info = client.table(st.secrets["SUPABASE_PATIENT_LOG_TABLE"]).select("*").eq("patient_id", st.session_state['patient_id']).execute()


if not log_info.data:
    st.info("No logs available yet. Please complete a daily log entry first.")
    st.stop()

else:
    logs = pd.DataFrame(log_info.data)
    
    # Ensure date column is in datetime format
    if 'date' in logs.columns:
        logs['date'] = pd.to_datetime(logs['date'], errors='coerce')

    # Remove any rows with invalid dates
    logs = logs.dropna(subset=['date'])


    # Summary stats
    st.subheader("Recovery Overview")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Days Logged", len(logs))
    with col2:
        avg_severity = logs['symptom_severity'].mean().round(1)
        st.metric("Average Symptom Severity", f"{avg_severity}/10")
    with col3:
        last_mood = logs.iloc[-1]['mood'] if 'mood' in logs.columns and not logs.empty else "N/A"
        st.metric("Most Recent Mood", last_mood)

    # Symptom severity over time
    st.subheader("Symptom Severity Over Time")
    if not logs.empty and 'date' in logs.columns and 'symptom_severity' in logs.columns:
        st.line_chart(
            data=logs.set_index('date')['symptom_severity'],
            use_container_width=True
        )

    # Symptoms frequency
    st.subheader("Most Common Symptoms")
    symptom_counts = {}
    if 'symptoms' in logs.columns:
        for symptoms in logs['symptoms'].dropna():
            for symptom in [s.strip() for s in str(symptoms).split(',') if s.strip()]:
                symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1

    if symptom_counts:
        import plotly.express as px
        df_symptoms = pd.DataFrame({
            'Symptom': list(symptom_counts.keys()),
            'Count': list(symptom_counts.values())
        }).sort_values('Count', ascending=False)
        
        fig = px.bar(
            df_symptoms, 
            x='Symptom', 
            y='Count',
            title="Symptom Frequency"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Show recent logs
    st.subheader("Recent Logs")
    if not logs.empty:
        # Select and format columns for display
        display_cols = ['date', 'symptom_severity', 'mood', 'sleep_quality', 'medication_taken']
        display_cols = [col for col in display_cols if col in logs.columns]
        
        if display_cols:
            st.dataframe(
                logs[display_cols].sort_values('date', ascending=False).head(10),
                column_config={
                    'date': st.column_config.DateColumn("Date"),
                    'symptom_severity': st.column_config.NumberColumn(
                        "Severity (1-10)", 
                        format="%d",
                        help="1 = Very mild, 10 = Extremely severe"
                    ),
                    'mood': "Mood",
                    'sleep_quality': "Sleep Quality",
                    'medication_taken': "Medication Taken"
                },
                hide_index=True,
                use_container_width=True
            )


