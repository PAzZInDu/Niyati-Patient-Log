import streamlit as st

def concussion_instructions():
    st.title("⚠️ Concussion Safety Instructions for Soccer Players")

    st.write(
        "These instructions must be followed immediately if a player is suspected of having a concussion during a match or training session."
    )

    st.divider()

    st.header("🚨 Immediate Actions on the Field")

    st.markdown("""
    **1. Stop the player immediately**  
    The player must not continue playing under any circumstance.

    **2. Remove the player from the field**  
    Even if the player says they are fine, they must leave the game.

    **3. Do NOT allow same-day return to play**  
    A concussed player should NEVER return to play on the same day.

    **4. Monitor symptoms closely**  
    Look for signs such as:
    - Headache  
    - Dizziness  
    - Confusion  
    - Nausea or vomiting  
    - Sensitivity to light or noise  
    - Blurred vision  
    """)

    st.divider()

    st.header("🏥 Medical Evaluation")

    st.markdown("""
    **5. Get medical assessment immediately**  
    The player must be evaluated by a qualified medical professional.

    **6. Follow medical advice strictly**  
    Do not rely on coach or player judgment for return-to-play decisions.
    """)

    st.divider()

    st.header("⏳ Recovery & Return to Play")

    st.markdown("""
    **7. Complete full physical and mental rest**  
    Avoid sports, intense studying, mobile phones, and bright screens during early recovery.

    **8. Gradual return-to-play protocol**  
    A player should only return through a step-by-step medical clearance process.

    **9. Final medical clearance is mandatory**  
    The player must be officially cleared by a doctor before returning to matches.
    """)

    st.divider()

    # Important instructions
    st.header("❗ Important Warning")
    st.error( "Ignoring concussion symptoms can lead to permanent brain damage or even death. Always take concussions seriously.")
    st.success("✅ Player safety is always the top priority.")

if __name__ == "__main__":
    concussion_instructions()
