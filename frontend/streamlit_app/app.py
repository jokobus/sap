import streamlit as st
import os
from datetime import datetime
import json
import time

# --- UTILITY FUNCTIONS ---

def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    if 'step' not in st.session_state:
        st.session_state.step = 'init'
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'cv_uploaded' not in st.session_state:
        st.session_state.cv_uploaded = False

def save_data():
    """Saves the collected user data to a JSON file."""
    script_dir = os.path.dirname(__file__)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(script_dir, "..", "data", "outputs", f"intake_{timestamp}.json")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(st.session_state.user_data, f, indent=4)
    st.success(f"Your information has been saved.")

def navigation_buttons(back_step=None, next_step=None, next_text="Continue"):
    """Creates standardized back and next buttons."""
    st.write("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if back_step:
            if st.button("⬅️ Back"):
                st.session_state.step = back_step
                st.rerun()
    with col2:
        if next_step:
            if st.button(f"{next_text} ➡️"):
                st.session_state.step = next_step
                st.rerun()

# --- UI BLOCKS ---

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
    with st.chat_message("assistant"):
        st.header("Upload your CV (Optional)")
        st.write("If you upload a CV, we can provide better matches. (Parsing functionality is under development).")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        with st.spinner('Uploading and processing...'):
            script_dir = os.path.dirname(__file__)
            upload_path = os.path.join(script_dir, "..", "data", "uploads", uploaded_file.name)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            with open(upload_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.user_data['cv_path'] = upload_path
            st.session_state.cv_uploaded = True
            time.sleep(1) # Simulate processing
        st.success("CV uploaded successfully!")

    navigation_buttons(back_step='basic_info_social', next_step='main_decision_tree', next_text="Continue to Main Questions")

def show_main_decision_tree():
    """The main decision tree for user status."""
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
    with st.chat_message("assistant"):
        st.header("Let's explore your interests for a new field.")
    st.session_state.user_data['interested_industries'] = st.text_input("Which topics or industries interest you most? (IT, design, social work, business, etc.)")
    st.session_state.user_data['skills_to_use'] = st.text_input("Which of your skills would you like to use more often?")
    st.session_state.user_data['preferred_environment_new'] = st.selectbox("What kind of work environment do you prefer?", ('Office', 'Hybrid', 'Fieldwork', 'Remote'))
    st.session_state.user_data['job_priorities'] = st.selectbox("What is most important to you in a job?", ('Salary', 'Purpose', 'Flexibility', 'Growth'))

    navigation_buttons(back_step='employee_questions', next_step='skills_block', next_text="Continue to Skills")

def show_skills_block():
    """Asks about user's skills."""
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
    back_step = 'student_questions' # Default
    if st.session_state.user_data.get('status') == 'Employee':
        if st.session_state.user_data.get('career_path_intention') == 'Switch to a new field':
            back_step = 'interests_block'
        else:
            back_step = 'employee_questions'

    # After skills, go to action selection hub instead of immediate suggestions
    navigation_buttons(back_step=back_step, next_step='action_selection', next_text="Select Action")

def show_action_selection():
    """Central hub after data entry where user picks desired action. Saves data once."""
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

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("⬅️ Back to Skills"):
            st.session_state.step = 'skills_block'
            st.rerun()
    with col2:
        disabled = action == "Select an action..."
        if st.button("Go ➡️", disabled=disabled):
            st.session_state.step = action_map[action]
            st.rerun()

def show_cv_suggestions():
    """Collects job description input and shows placeholder tailored CV advice."""
    with st.chat_message("assistant"):
        st.header("Tailored CV / Resume Suggestions")
        st.write("Paste the job description text so that we can tailor your CV. ")

    job_title = st.text_input("Job title (optional)")
    job_description = st.text_area("Job description (paste text here)", height=200)

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("⬅️ Back to Action Selection"):
            st.session_state.step = 'action_selection'
            st.rerun()
    with col2:
        if st.button("Generate Suggestions ➡️"):
            if not job_description.strip():
                st.warning("Please paste a job description to generate tailored suggestions.")
            else:
                with st.chat_message("assistant"):
                    st.subheader("Suggested improvements (preview)")
                    st.write("This is a lightweight, rule-based preview. Advanced AI-tailoring can be added later.")
                    # Very simple keyword extraction preview
                    jd = job_description.lower()
                    cues = {
                        'python': "Highlight Python projects and quantify impact (e.g., performance gains, data size).",
                        'excel': "Mention Excel proficiency with formulas, pivot tables, or VBA if applicable.",
                        'management': "Emphasize leadership, stakeholder communication, and project outcomes.",
                        'sql': "Add SQL queries, databases used, and data volumes handled.",
                        'sales': "Quantify results (conversion rate, pipeline growth, revenue).",
                        'design': "List tools (Figma, Adobe) and attach a folio link if available.",
                        'data': "Include datasets scale, models/analytics, and decisions enabled.",
                        'cloud': "Name providers (AWS, Azure, GCP) and services used.",
                        'javascript': "Mention frameworks and components built; include performance or UX metrics.",
                        'customer': "Showcase customer-facing wins: NPS, retention, or satisfaction improvements.",
                        'teaching': "Add mentorship/training experience, curricula, or outcomes.",
                        'research': "Summarize methods, citations, or publications and your role.",
                        'project': "Ensure bullets start with active verbs and end with measurable outcomes.",
                        'team': "Reflect collaboration, cross-functional work, and communication cadence.",
                        'remote': "Include async tools, time zones, and self-management examples."
                    }
                    hits = [tip for kw, tip in cues.items() if kw in jd]
                    if not hits:
                        st.write("No specific keywords detected. General advice:")
                        hits = [
                            "Use strong action verbs and quantify outcomes (%, $, time saved).",
                            "Align top bullets with the job's must-have requirements.",
                            "Keep it concise: 1–2 pages, clean layout, consistent tense and punctuation.",
                        ]
                    for h in hits:
                        st.markdown(f"- {h}")
    
    st.write("\n")
    navigation_buttons(back_step='action_selection', next_step=None)

def show_training_recommendations():
    """Placeholder for future training recommendations feature."""
    with st.chat_message("assistant"):
        st.header("Training Program Recommendations (Coming Soon)")
        st.write("Personalized courses and learning paths will appear here based on your goals and gaps.")
    navigation_buttons(back_step='action_selection', next_step=None)

def show_job_suggestions():
    """Displays job suggestions based on inputs."""
    with st.chat_message("assistant"):
        st.header("Job Suggestions")
        st.write("Based on your answers, here are some job categories that might be a good fit for you.")
        st.write("(This is a simplified matching logic for demonstration.)")

    # Simple logic to suggest categories.
    suggestions = set()
    user_info = st.session_state.user_data
    if user_info.get('status') == 'Student' or 'IT' in user_info.get('interested_industries', ''):
        suggestions.add("IT / Data / Analysis → Logical, technical, numbers-oriented")
    if 'business' in user_info.get('interested_industries', ''):
        suggestions.add("Business / Project Management → Organized, communicative, goal-driven")
    if 'design' in user_info.get('interested_industries', ''):
        suggestions.add("Creative / Media / Design → Imaginative, artistic, tool-savvy")
    if 'social' in user_info.get('interested_industries', ''):
        suggestions.add("Social / Education / Healthcare → Empathetic, helpful, purpose-driven")
    if not suggestions:
        suggestions.add("Business / Project Management → Organized, communicative, goal-driven")
        suggestions.add("Sales / Customer Service → Outgoing, social, persuasive")

    for suggestion in suggestions:
        st.markdown(f"- {suggestion}")

    # Always allow returning directly to action selection hub
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("⬅️ Back to Action Selection"):
            st.session_state.step = 'action_selection'
            st.rerun()
    with col2:
        if st.button("Return to Skills"):
            # Determine appropriate skills back path (skills block already central)
            st.session_state.step = 'skills_block'
            st.rerun()

def show_feedback_phase():
    """Final phase for user feedback and next steps."""
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


# --- MAIN APP LOGIC ---

def main():
    """Main function to run the Streamlit app."""
    initialize_session_state()

    step_functions = {
        'init': show_init_message,
        'basic_info_personal': show_basic_info_personal,
        'basic_info_social': show_basic_info_social,
        'cv_upload': show_cv_upload,
        'main_decision_tree': show_main_decision_tree,
        'student_questions': show_student_questions,
        'employee_questions': show_employee_questions,
        'unemployed_questions': show_unemployed_questions,
        'interests_block': show_interests_block,
        'skills_block': show_skills_block,
    'action_selection': show_action_selection,
    'job_suggestions': show_job_suggestions,
    'cv_suggestions': show_cv_suggestions,
    'training_recommendations': show_training_recommendations,
    }
    
    if st.session_state.step in step_functions:
        step_functions[st.session_state.step]()

if __name__ == "__main__":
    main()
