import streamlit as st
from dotenv import load_dotenv

# Import modular tab components
from tabs import (
    render_profile_tab,
    render_skills_tab,
    render_job_search_tab,
    render_reach_out_tab
)

# ---------------------------
# Streamlit page config + session state
# ---------------------------
st.set_page_config(page_title="Modular Job Finder", layout="wide")
load_dotenv()

if "candidate_json" not in st.session_state:
    st.session_state["candidate_json"] = None
if "resume_json" not in st.session_state:
    st.session_state["resume_json"] = None
if "linkedin_json" not in st.session_state:
    st.session_state["linkedin_json"] = None
if "github_json" not in st.session_state:
    st.session_state["github_json"] = None
if "resume_bytes" not in st.session_state:
    st.session_state["resume_bytes"] = None
if "linkedin_bytes" not in st.session_state:
    st.session_state["linkedin_bytes"] = None
if "github_username" not in st.session_state:
    st.session_state["github_username"] = ""
if "job_queries" not in st.session_state:
    st.session_state["job_queries"] = []
if "job_results" not in st.session_state:
    st.session_state["job_results"] = {}
if "collected_jobs" not in st.session_state:
    st.session_state["collected_jobs"] = []
if "ranked_jobs" not in st.session_state:
    st.session_state["ranked_jobs"] = []
if "selected_job" not in st.session_state:
    st.session_state["selected_job"] = None
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Profile"

# ---------------------------
# Sidebar: tabs + global controls
# ---------------------------
st.sidebar.title("Workspace")
st.session_state["active_tab"] = st.sidebar.radio(
    "Select page",
    ["Profile", "What Am I good at?", "Job Search", "Reach out"],
    index=["Profile", "What Am I good at?", "Job Search", "Reach out"].index(st.session_state.get("active_tab", "Profile"))
)
st.sidebar.markdown("---")
pages = st.sidebar.number_input("Pages per query", value=2, min_value=1, max_value=10, key="sid_pages")
results_per_page = st.sidebar.number_input("Results per page", value=5, min_value=1, max_value=25, key="sid_results")
max_workers = st.sidebar.number_input("Scraper workers", value=4, min_value=1, max_value=16, key="sid_workers")
st.sidebar.markdown("---")
st.sidebar.caption("Save profile in Profile tab. Use Job Search to generate queries & run scraper. Use Rank to compute relevance.")

# ---------------------------
# Main header
# ---------------------------
st.title("SkillMatch — AI-powered Skills & Job Finder")
st.write("Profile-driven job discovery. UI logic is separated from business logic in services/ and ui_helpers.")

# ---------------------------
# Route to appropriate tab
# ---------------------------
if st.session_state["active_tab"] == "Profile":
    render_profile_tab()

elif st.session_state["active_tab"] == "What Am I good at?":
    render_skills_tab()

elif st.session_state["active_tab"] == "Job Search":
    render_job_search_tab()

elif st.session_state["active_tab"] == "Reach out":
    render_reach_out_tab()

# Footer
st.markdown("---")
st.caption("This app.py contains only UI and file reading logic. Implement business logic in services/ and UI helpers in ui_helpers.py")