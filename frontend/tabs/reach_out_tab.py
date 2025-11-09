"""
Reach Out Tab - Contact and communication functionality
"""
import streamlit as st
import pandas as pd


def render_reach_out_tab():
    """
    Render the Reach out tab - linked to selected job
    Shows contact information and message templates
    """
    st.header("Reach out")
    
    selected = st.session_state.get("selected_job")
    
    if not selected:
        st.info("No job selected. From the Job Search tab, click 'Open Reach out' on a job card to bring it here.")
        
        if st.session_state.get("job_queries"):
            st.write("Or pick a job to demo reach-out UI:")
            q = st.session_state["job_queries"][0]
            df = st.session_state["job_results"].get(0, pd.DataFrame())
            if not df.empty:
                if st.button("Select first job from first query (demo)"):
                    st.session_state["selected_job"] = {
                        "query_index": 0, 
                        "job_index": 0, 
                        "job": df.iloc[0].to_dict()
                    }
                    st.rerun()
        return
    
    st.write("Selected job (dev placeholder):")
    st.json(selected["job"])
    
    st.markdown("**Placeholder for reach-out logic** — developer tasks:")
    st.write("- Use job posting URL to extract recruiter/contact names and LinkedIn profiles.")
    st.write("- Show recommended message templates, AB tests, and contact priority.")
    st.write("- Allow export of contact list as CSV or send messages via integrated channels (LinkedIn/email).")
    st.warning("This page currently does not fetch contacts. Implement recruiter extraction & auth flows in backend.")
