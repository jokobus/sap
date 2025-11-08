import streamlit as st
import json
import os
from datetime import datetime

def initialize_session_state():
    """Initializes the session state variables."""
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'education_entries' not in st.session_state:
        st.session_state.education_entries = [{'title': '', 'university': '', 'start_time': '', 'end_time': '', 'location': '', 'description': ''}]
    if 'experience_entries' not in st.session_state:
        st.session_state.experience_entries = [{'title': '', 'company': '', 'start_time': '', 'end_time': '', 'location': '', 'description': ''}]

def save_data():
    """Saves the user data to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Get the directory of the current script
    script_dir = os.path.dirname(__file__)
    filename = os.path.join(script_dir, "..", "data", "outputs", f"intake_{timestamp}.json")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(st.session_state.user_data, f, indent=4)
    st.success(f"Data saved successfully to {filename}")

def collect_dynamic_entries(entry_type, entries_key, title_label, name_label):
    """Collects multiple entries for education or experience."""
    st.subheader(f"Please add your {title_label.lower()}.")
    
    if entries_key not in st.session_state:
        st.session_state[entries_key] = [{'title': '', 'name': '', 'start_time': '', 'end_time': '', 'location': '', 'description': ''}]

    entries = st.session_state[entries_key]

    for i, entry in enumerate(entries):
        st.markdown(f"---")
        entry['title'] = st.text_input(f"{title_label} Title", value=entry.get('title', ''), key=f"{entries_key}_title_{i}")
        entry['name'] = st.text_input(name_label, value=entry.get('name', ''), key=f"{entries_key}_name_{i}")
        entry['start_time'] = st.text_input("Start Date (e.g., YYYY-MM)", value=entry.get('start_time', ''), key=f"{entries_key}_start_{i}")
        entry['end_time'] = st.text_input("End Date (e.g., YYYY-MM or 'Present')", value=entry.get('end_time', ''), key=f"{entries_key}_end_{i}")
        entry['location'] = st.text_input("Location", value=entry.get('location', ''), key=f"{entries_key}_location_{i}")
        entry['description'] = st.text_area("Description", value=entry.get('description', ''), key=f"{entries_key}_desc_{i}", height=100)

    if st.button(f"Add another {title_label.lower()}", key=f"add_{entries_key}"):
        entries.append({'title': '', 'name': '', 'start_time': '', 'end_time': '', 'location': '', 'description': ''})
        st.rerun()

def main():
    """Main function to run the Streamlit app."""
    st.title("Welcome! Let's get to know you.")
    
    initialize_session_state()

    # Progress Bar
    progress = st.session_state.step / 5.0
    st.progress(progress)

    # Step 0: Basic Information
    if st.session_state.step == 0:
        st.header("Let's start with some basic information.")
        st.session_state.user_data['firstname'] = st.text_input("First Name")
        st.session_state.user_data['lastname'] = st.text_input("Last Name")
        st.session_state.user_data['dob'] = str(st.date_input("Date of Birth", min_value=datetime(1950, 1, 1)))
        st.session_state.user_data['email'] = st.text_input("Email Address")
        st.session_state.user_data['phone'] = st.text_input("Phone Number")
        st.header("Your online presence")
        st.session_state.user_data['linkedin'] = st.text_input("LinkedIn Profile URL")
        st.session_state.user_data['instagram'] = st.text_input("Instagram Profile URL")
        st.session_state.user_data['facebook'] = st.text_input("Facebook Profile URL")
        
        if st.button("Next: Upload CV"):
            st.session_state.step = 1
            st.rerun()

    # Step 1: CV Upload
    elif st.session_state.step == 1:
        st.header("Great! Now, please upload your CV/Resume.")
        st.write("It helps us to get a better picture of you.")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            script_dir = os.path.dirname(__file__)
            upload_path = os.path.join(script_dir, "..", "data", "uploads", uploaded_file.name)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            with open(upload_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.user_data['cv_path'] = upload_path
            st.success("CV uploaded successfully!")
        
        if st.button("Next: Your Status"):
            st.session_state.step = 2
            st.rerun()

    # Step 2: Student or Employee
    elif st.session_state.step == 2:
        st.header("What is your current professional status?")
        status = st.radio("This helps us to ask the right questions.", ('Student', 'Employee'))
        st.session_state.user_data['status'] = status
        
        if st.button("Next: Details"):
            if status == 'Student':
                st.session_state.step = 3
            else:
                st.session_state.step = 4
            st.rerun()

    # Step 3: Student Questions
    elif st.session_state.step == 3:
        st.header("Tell us about your education.")
        st.session_state.user_data['current_degree'] = st.text_input("What is your current degree program?")
        st.session_state.user_data['school_degree'] = st.text_input("What was your highest school degree?")
        
        collect_dynamic_entries("other_degrees", "education_entries", "Other Degree", "University/School Name")
        collect_dynamic_entries("working_experience", "experience_entries", "Working Experience", "Company Name")
        
        if st.button("Finish"):
            st.session_state.user_data['other_degrees'] = st.session_state.education_entries
            st.session_state.user_data['working_experience'] = st.session_state.experience_entries
            st.session_state.step = 5
            st.rerun()

    # Step 4: Employee Questions
    elif st.session_state.step == 4:
        st.header("Tell us about your professional life.")
        st.session_state.user_data['current_job'] = st.text_input("What is your current job title?")
        
        collect_dynamic_entries("previous_jobs", "experience_entries", "Previous Job", "Company Name")
        collect_dynamic_entries("university_degrees", "education_entries", "University Degree", "University Name")

        if st.button("Finish"):
            st.session_state.user_data['previous_jobs'] = st.session_state.experience_entries
            st.session_state.user_data['university_degrees'] = st.session_state.education_entries
            st.session_state.step = 5
            st.rerun()

    # Step 5: Save and Finish
    elif st.session_state.step == 5:
        st.balloons()
        st.header("Thank you for your time!")
        st.write("We have collected your information. Here is a summary:")
        st.json(st.session_state.user_data)
        save_data()
        if st.button("Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
