"""Reach Out Tab - Handles feedback and next steps communication"""
import streamlit as st


def show_feedback_phase():
    """Final phase for user feedback and next steps."""
    from utils import save_data
    
    with st.chat_message("assistant"):
        st.header("Feedback & Next Steps")
        st.balloons()
        st.write("Thank you for completing your profile!")
    
    save_data()

    with st.expander("See the data we collected"):
        st.json(st.session_state.user_data)

    with st.chat_message("assistant"):
        st.subheader("What would you like to see next?")
    
    feedback_option = st.selectbox("Choose an option", [
        "Select an option...",
        "Show me job postings that fit my profile (coming soon!)",
        "Give me tailored CV/resume suggestions (coming soon!)",
        "Recommend training programs for me (coming soon!)"
    ])

    if feedback_option != "Select an option...":
        st.info("This feature is currently under development. Stay tuned!")

    if st.button("Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
