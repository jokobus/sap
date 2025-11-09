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
# Streamlit page configuration
# ---------------------------
st.set_page_config(page_title="Resume → Job Matches", layout="wide")
load_dotenv()

# Initialize session state
if "candidate_json" not in st.session_state:
    st.session_state["candidate_json"] = None
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
if "selected_job" not in st.session_state:
    st.session_state["selected_job"] = None
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Profile"

# ---------------------------
# Sidebar: tabs + global controls
# ---------------------------
st.sidebar.title("Workspace")
tab_choice = st.sidebar.radio(
    "Select page",
    ["Profile", "What Am I good at?", "Job Search", "Reach out"],
    index=["Profile", "What Am I good at?", "Job Search", "Reach out"].index(st.session_state.get("active_tab", "Profile"))
)
st.session_state["active_tab"] = tab_choice

# Keep some global quick controls in sidebar (optional)
st.sidebar.markdown("---")
st.sidebar.header("Scraper settings (global)")
pages = st.sidebar.number_input("Pages per query", value=2, min_value=1, max_value=10, key="sid_pages")
results_per_page = st.sidebar.number_input("Results per page", value=5, min_value=1, max_value=25, key="sid_results")
max_workers = st.sidebar.number_input("Scraper workers", value=4, min_value=1, max_value=16, key="sid_workers")
st.sidebar.markdown("---")
st.sidebar.caption("Use the Profile tab to upload and save a profile. Use Job Search tab to generate queries & run scraper.")

# ---------------------------
# Main header
# ---------------------------
st.title("Job Finder — Profile-driven job discovery")
st.write("Save your profile, then switch to the other tabs to explore skills, search jobs, and prepare reach-outs.")

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
st.caption("Notes: The app expects `parse_all`, `extract_job_search_queries`, and `scrape_linkedin_jobs` to be importable. If absent, fallback heuristics are used. Tabs 'What Am I good at?' and 'Reach out' are placeholders for developer logic.")
