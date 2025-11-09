"""Skills Tab - Handles user skills and competencies assessment"""
import streamlit as st


def show_skills_block():
    """Asks about user's skills."""
    from utils import navigation_buttons
    
    with st.chat_message("assistant"):
        st.header("Tell us about your skills.")
    st.session_state.user_data['top_strengths'] = st.text_input("What are your top three strengths or skills? (comma-separated)")
    st.session_state.user_data['tools_programs'] = st.text_input("Which tools or programs can you use confidently? (Excel, Photoshop, CAD, etc.)")
    st.session_state.user_data['work_style'] = st.selectbox("How do you prefer to work?", ('In a team', 'Independently', 'A mix of both (Hybrid)'))
    open_to_courses = st.radio("Are you open to learning new tools or taking short courses?", ('Yes', 'No'))
    st.session_state.user_data['open_to_short_courses'] = open_to_courses

    if open_to_courses == 'Yes':
        st.info("Excellent! We can suggest suitable courses for you.")

    # Determine the correct "back" step
    back_step = 'student_questions'  # Default
    if st.session_state.user_data.get('status') == 'Employee':
        if st.session_state.user_data.get('career_path_intention') == 'Switch to a new field':
            back_step = 'interests_block'
        else:
            back_step = 'employee_questions'

    # After skills, go to action selection hub instead of immediate suggestions
    navigation_buttons(back_step=back_step, next_step='action_selection', next_text="Select Action")


def show_action_selection():
    """Central hub after data entry where user picks desired action. Saves data once."""
    from utils import save_data
    
    with st.chat_message("assistant"):
        st.header("Select Your Next Action")
        st.write("Your profile is ready. Choose what you'd like to do next.")

    # Ensure data saved once (could add guard if needed)
    if 'data_saved' not in st.session_state:
        save_data()
        st.session_state.data_saved = True

    with st.expander("Preview collected data"):
        st.json(st.session_state.user_data)

    action = st.selectbox(
        "What would you like to get?",
        [
            "Select an action...",
            "Show me job postings that fit my profile (coming soon!)",
            "Give me tailored CV/resume suggestions (coming soon!)",
            "Recommend training programs for me (coming soon!)"
        ]
    )

    # Map selection to next step
    action_map = {
        "Show me job postings that fit my profile (coming soon!)": 'job_suggestions',
        "Give me tailored CV/resume suggestions (coming soon!)": 'cv_suggestions',
        "Recommend training programs for me (coming soon!)": 'training_recommendations'
    }

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back to Skills"):
            st.session_state.step = 'skills_block'
            st.rerun()
    with col2:
        disabled = action == "Select an action..."
        if st.button("Go ➡️", disabled=disabled):
            st.session_state.step = action_map[action]
            st.rerun()
