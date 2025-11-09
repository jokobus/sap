"""Profile Tab - Handles user profile data collection"""
import streamlit as st
from datetime import datetime


def show_init_message():
    """Displays the initial welcome message."""
    with st.chat_message("assistant"):
        st.title("Job-Matching Assistant")
        st.write("Welcome! This assistant will help you find job suggestions tailored to your profile.")
        st.info("Providing personal data is optional but helps improve accuracy. You can skip any field by leaving it blank and pressing the 'Continue' button.")
    if st.button("Let's get started ➡️"):
        st.session_state.step = 'basic_info_personal'
        st.rerun()


def show_basic_info_personal():
    """Displays the personal data fields."""
    from utils import navigation_buttons
    
    with st.chat_message("assistant"):
        st.header("First, some basic information (Optional)")
        st.write("This information is only stored on our own servers and not fed into the AI.")
    
    st.text_input("Name")
    st.date_input("Birthday / Birth year", min_value=datetime(1950, 1, 1))
    st.text_input("Email address")
    st.text_input("Phone number")
    st.text_input("ZIP code / City")
    
    navigation_buttons(back_step='init', next_step='basic_info_social', next_text="Continue to Social Media")


def show_basic_info_social():
    """Displays social media link fields."""
    from utils import navigation_buttons
    
    with st.chat_message("assistant"):
        st.header("Your Online Presence (Optional)")
        st.write("Links to your professional or social profiles can sometimes help us find a better match.")
    st.session_state.user_data['linkedin'] = st.text_input("LinkedIn")
    st.session_state.user_data['xing'] = st.text_input("Xing")
    st.session_state.user_data['instagram'] = st.text_input("Instagram")
    st.session_state.user_data['facebook'] = st.text_input("Facebook")
    st.session_state.user_data['other_social'] = st.text_input("Any other?")

    navigation_buttons(back_step='basic_info_personal', next_step='cv_upload', next_text="Continue to CV Upload")


def show_cv_upload():
    """Dedicated page for CV upload."""
    import os
    import time
    from utils import navigation_buttons
    
    with st.chat_message("assistant"):
        st.header("Upload your CV (Optional)")
        st.write("If you upload a CV, we can provide better matches. (Parsing functionality is under development).")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        with st.spinner('Uploading and processing...'):
            script_dir = os.path.dirname(os.path.dirname(__file__))
            upload_path = os.path.join(script_dir, "data", "uploads", uploaded_file.name)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            with open(upload_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.user_data['cv_path'] = upload_path
            st.session_state.cv_uploaded = True
            time.sleep(1)  # Simulate processing
        st.success("CV uploaded successfully!")

    navigation_buttons(back_step='basic_info_social', next_step='main_decision_tree', next_text="Continue to Main Questions")


def show_main_decision_tree():
    """The main decision tree for user status."""
    from utils import navigation_buttons
    
    with st.chat_message("assistant"):
        st.header("Now, let's talk about your current situation.")
        status = st.radio("What are you currently doing?", ('Student', 'Employee', 'Unemployed / Looking for a job'), key="status_radio")
    
    st.session_state.user_data['status'] = status
    
    next_step = None
    if status == 'Student':
        next_step = 'student_questions'
    elif status == 'Employee':
        next_step = 'employee_questions'
    elif status == 'Unemployed / Looking for a job':
        next_step = 'unemployed_questions'

    navigation_buttons(back_step='cv_upload', next_step=next_step)


def show_student_questions():
    """Handles questions for students."""
    from utils import navigation_buttons
    
    with st.chat_message("assistant"):
        st.write("Great, a student! Let's get some details.")
    st.session_state.user_data['current_degree'] = st.text_input("What degree are you currently pursuing?")
    st.session_state.user_data['university'] = st.text_input("Which university are you studying at?")
    st.session_state.user_data['graduation_date'] = st.text_input("When do you plan to graduate? (e.g., YYYY-MM)")
    has_experience = st.radio("Do you already have any practical experience in your field?", ('Yes', 'No'))
    if has_experience == 'Yes':
        st.session_state.user_data['practical_experience'] = st.text_area("Please describe (e.g., internship, student job)")
    else:
        st.session_state.user_data['open_to_internship'] = st.selectbox("Are you open to internships or entry-level positions?", ('Yes', 'No', 'Not sure'))
    
    navigation_buttons(back_step='main_decision_tree', next_step='skills_block', next_text="Continue to Skills")


def show_employee_questions():
    """Handles questions for employees."""
    from utils import navigation_buttons
    
    with st.chat_message("assistant"):
        st.write("An employee! Let's hear about your current role.")
    st.session_state.user_data['current_position'] = st.text_input("What is your current position or job title?")
    st.session_state.user_data['time_in_position'] = st.text_input("How long have you been in this position?")
    st.session_state.user_data['likes_about_job'] = st.text_area("What do you like most about your current job?")
    career_path = st.radio("Would you like to stay in the same field or switch to something new?", ('Stay in the same field', 'Switch to a new field'))
    st.session_state.user_data['career_path_intention'] = career_path

    next_step = 'skills_block' if career_path == 'Stay in the same field' else 'interests_block'
    next_text = "Continue to Skills" if next_step == 'skills_block' else "Continue to Interests"
    
    navigation_buttons(back_step='main_decision_tree', next_step=next_step, next_text=next_text)


def show_unemployed_questions():
    """Handles questions for unemployed users."""
    from utils import navigation_buttons
    
    with st.chat_message("assistant"):
        st.write("Looking for a new opportunity is exciting! Let's find the right fit.")
    st.session_state.user_data['desired_job'] = st.text_input("What kind of job are you looking for?")
    st.session_state.user_data['top_three_skills'] = st.text_input("What are your top three skills? (comma-separated)")
    st.session_state.user_data['preferred_environment'] = st.selectbox("What work environment do you prefer?", ('Office', 'Remote', 'Hybrid', 'Outdoors', 'Workshop'))
    st.session_state.user_data['experience_in_field'] = st.text_input("How much experience do you have in your desired field?")
    open_to_learning = st.radio("Are you open to learning or re-skilling for a better match?", ('Yes', 'No'))
    st.session_state.user_data['open_to_reskilling'] = open_to_learning
    
    if open_to_learning == 'Yes':
        st.info("That's great! We can suggest some learning paths later.")
    
    navigation_buttons(back_step='main_decision_tree', next_step='job_suggestions', next_text="Continue to Job Suggestions")


def show_interests_block():
    """Asks about user's interests."""
    from utils import navigation_buttons
    
    with st.chat_message("assistant"):
        st.header("Let's explore your interests for a new field.")
    st.session_state.user_data['interested_industries'] = st.text_input("Which topics or industries interest you most? (IT, design, social work, business, etc.)")
    st.session_state.user_data['skills_to_use'] = st.text_input("Which of your skills would you like to use more often?")
    st.session_state.user_data['preferred_environment_new'] = st.selectbox("What kind of work environment do you prefer?", ('Office', 'Hybrid', 'Fieldwork', 'Remote'))
    st.session_state.user_data['job_priorities'] = st.selectbox("What is most important to you in a job?", ('Salary', 'Purpose', 'Flexibility', 'Growth'))

    navigation_buttons(back_step='employee_questions', next_step='skills_block', next_text="Continue to Skills")
