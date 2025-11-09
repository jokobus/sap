"""Job Search Tab - Handles job matching and suggestions"""
import streamlit as st


def show_job_suggestions():
    """Displays job suggestions based on inputs."""
    from utils import navigation_buttons
    
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
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back to Action Selection"):
            st.session_state.step = 'action_selection'
            st.rerun()
    with col2:
        if st.button("Return to Skills"):
            # Determine appropriate skills back path (skills block already central)
            st.session_state.step = 'skills_block'
            st.rerun()


def show_cv_suggestions():
    """Collects job description input and shows placeholder tailored CV advice."""
    from utils import navigation_buttons
    
    with st.chat_message("assistant"):
        st.header("Tailored CV / Resume Suggestions")
        st.write("Paste the job description text so that we can tailor your CV. ")

    job_title = st.text_input("Job title (optional)")
    job_description = st.text_area("Job description (paste text here)", height=200)

    col1, col2 = st.columns([1, 1])
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
    from utils import navigation_buttons
    
    with st.chat_message("assistant"):
        st.header("Training Program Recommendations (Coming Soon)")
        st.write("Personalized courses and learning paths will appear here based on your goals and gaps.")
    navigation_buttons(back_step='action_selection', next_step=None)
