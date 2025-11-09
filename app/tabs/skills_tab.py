"""
Skills Tab - "What Am I good at?" analysis
"""
import streamlit as st


def render_skills_tab():
    """
    Render the "What Am I good at?" tab
    Shows skills analysis, strengths, weaknesses, and suggested roles
    """
    st.header("What Am I good at?")
    st.info("Placeholder: insert analysis logic here (skills extraction, TL;DR, strengths, weakness, suggested roles).")
    
    st.write("Developer notes / TODOs:")
    st.write("- Use `candidate_json` from session to build skill clusters, mapped seniority, and example roles.")
    st.write("- Show hoverable sources for each detected skill (UI: small info icon with source).")
    
    # Quick demo: list detected skills (best-effort)
    candidate_json = st.session_state.get("candidate_json") or {}
    skills = candidate_json.get("skills", [])
    
    if skills:
        st.write("Detected skills (raw):")
        st.write(skills)
    else:
        st.info("No skills detected. Save a profile first in the Profile tab.")
