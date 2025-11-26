# quiz.py
import streamlit as st

def show_quiz():
    st.title("🧠 Safety Knowledge Quiz")
    st.write("Test your knowledge about football safety protocols and best practices.")

    # Initialize session state
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
        st.session_state.score = 0
        st.session_state.q1 = None
        st.session_state.q2 = None

    # SHOW QUIZ ONLY IF NOT SUBMITTED
    if not st.session_state.quiz_submitted:

        st.header("Safety Quiz")

        st.subheader("Question 1: You can Only Get a Concussion From a Clash of Heads")
        st.session_state.q1 = st.radio(
            "You can Only Get a Concussion From a Clash of Heads",
            ["Yes", "No"],
            index=None
        )

        st.subheader("Question 2: After diagnosed a concussion, a player can be allowed to play again")
        st.session_state.q2 = st.radio(
            "After diagnosed a concussion, a player can be allowed to play again",
            ["Yes", "No"],
            index=None
        )

        submitted = st.button("Submit Quiz")

        if submitted:
            if st.session_state.q1 is None or st.session_state.q2 is None:
                st.warning("⚠️ Please answer both questions!")
            else:
                st.session_state.quiz_submitted = True
                st.session_state.score = 0

                if st.session_state.q1 == "No":
                    st.session_state.score += 1
                    st.success("✅ Correct! The answer to question 1 is 'No'")
                else:
                    st.error("❌ Incorrect. The correct answer is 'No'")

                if st.session_state.q2 == "No":
                    st.session_state.score += 1
                    st.success("✅ Correct! The answer to question 2 is 'No'")
                else:
                    st.error("❌ Incorrect. The correct answer is 'No'")

                st.rerun()   # Hides submit button immediately

    # SHOW RESULT AFTER SUBMISSION
    else:
        st.success(f"🎉 You scored {st.session_state.score} out of 2!")

        if st.button("Retake Quiz"):
            st.session_state.quiz_submitted = False
            st.session_state.score = 0
            st.session_state.q1 = None
            st.session_state.q2 = None
            st.rerun()

    
if __name__ == "__main__":
    show_quiz()