"""
Profile Tab - Upload and save candidate profile
"""
import streamlit as st
import asyncio
from typing import Optional

try:
    from aggregator import parse_all
except Exception:
    parse_all = None


def run_parse_and_save(resume_bytes: Optional[bytes], linkedin_bytes: Optional[bytes], github_username: str):
    """
    Call parse_all if available, otherwise build a demo candidate_json. 
    Store into session_state.
    """
    try:
        if parse_all is not None:
            # parse_all might be async or sync; handle both
            if asyncio.iscoroutinefunction(parse_all):
                candidate_json = asyncio.run(parse_all(resume_bytes, linkedin_bytes, github_username))
            else:
                candidate_json = parse_all(resume_bytes, linkedin_bytes, github_username)
        else:
            candidate_json = {
                "contact_info": {"name": "Unknown", "location": "", "headline": ""},
                "skills": [{"skills": ["Python", "Machine Learning", "Data Science"]}],
                "data_sources": []
            }
        st.session_state["candidate_json"] = candidate_json
        st.success("Profile parsed and saved to session.")
    except Exception as e:
        st.error(f"Parsing failed: {e}")
        st.session_state["candidate_json"] = None


def render_profile_tab():
    """
    Render the Profile tab - upload & save functionality
    """
    st.header("Profile — upload & save")
    col1, col2 = st.columns([2, 1])

    with col1:
        resume_file = st.file_uploader(
            "Upload resume PDF", 
            type=["pdf"], 
            key="profile_resume"
        )
        linkedin_file = st.file_uploader(
            "Upload LinkedIn profile PDF", 
            type=["pdf"], 
            key="profile_linkedin"
        )
        github_username = st.text_input(
            "GitHub username (optional)", 
            value=st.session_state.get("github_username", ""), 
            key="profile_github"
        )
        extra_notes = st.text_area(
            "Optional notes (internal)", 
            value="", 
            help="Add any notes you want the parser to consider (dev-only)"
        )

    with col2:
        st.markdown("### Quick preview")
        if st.session_state.get("candidate_json"):
            st.json(st.session_state["candidate_json"])
        else:
            st.info("No saved profile. Upload a resume or LinkedIn PDF and click Save Profile.")

    if st.button("Save Profile"):
        if not (resume_file or linkedin_file or github_username):
            st.error("Please upload at least a resume or LinkedIn PDF or provide a GitHub username.")
        else:
            st.session_state["resume_bytes"] = resume_file.read() if resume_file else None
            st.session_state["linkedin_bytes"] = linkedin_file.read() if linkedin_file else None
            st.session_state["github_username"] = github_username
            with st.spinner("Parsing candidate profile..."):
                run_parse_and_save(
                    st.session_state["resume_bytes"], 
                    st.session_state["linkedin_bytes"], 
                    github_username
                )
            # clear old job queries/results because profile changed
            st.session_state["job_queries"] = []
            st.session_state["job_results"] = {}
            st.session_state["selected_job"] = None
