"""
Skills Tab - "What Am I good at?" analysis using Gemini AI

This module uses Gemini AI to analyze candidate profiles from:
- Resume parser (parsed PDF data)
- LinkedIn profile scraper
- GitHub analyzer (portfolio analysis)

The AI generates a comprehensive skills analysis including:
1. Professional summary paragraph
2. Technical strengths by category
3. Experience depth calculations
4. Project expertise highlights
5. Career role suggestions

Results are cached to avoid repeated API calls.
"""
import streamlit as st
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

SKILLS_ANALYSIS_PROMPT = """
You are a career counselor analyzing a candidate's profile to answer "What am I good at?".

Analyze the following candidate data and provide a comprehensive skills analysis in Markdown format:

## CANDIDATE DATA:
{candidate_json}

## YOUR RESPONSE MUST INCLUDE:

### 1. Professional Summary (1-2 paragraphs)
Write a compelling summary of the candidate's expertise, highlighting their educational background, current role, years of experience, and key technical domains.

### 2. Core Technical Strengths (organized by category)
List skills grouped by category (e.g., Machine Learning, Programming Languages, Tools & Frameworks). For each skill, indicate data sources in parentheses (resume/linkedin/github).

### 3. Experience Depth
Calculate approximate years of experience in major domains (e.g., "Machine Learning & AI: 3 years", "Software Engineering: 4 years").

### 4. Project Expertise & Portfolio (top 5-6 projects)
Highlight key projects with brief descriptions and technologies used. Mention which source (resume/linkedin/github) each project comes from.

### 5. Suggested Career Roles (top 5)
List suitable job titles with fit level (Strong/Moderate) and reasoning based on skills and experience.

---
Format your response in clean Markdown with headers, bullet points, and emojis (📊 💪 🚀 🎯) for visual appeal.
"""


def analyze_with_gemini(candidate_json: dict) -> str:
    """Use Gemini to analyze candidate profile and generate skills analysis."""
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return (
            "⚠️ No API key found for Gemini.\n"
            "Set environment variable `GOOGLE_API_KEY` (or `GEMINI_API_KEY`).\n"
            "Example PowerShell: `$env:GOOGLE_API_KEY='your-key-here'` then restart Streamlit."
        )

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = SKILLS_ANALYSIS_PROMPT.format(
            candidate_json=json.dumps(candidate_json, indent=2)
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error analyzing profile: {e}\n\nIf this persists, verify the model name or regenerate your API key."


def render_skills_tab():
    """Render the "What Am I good at?" tab with AI-powered analysis."""
    st.header("What Am I good at?")
    
    candidate_json = st.session_state.get("candidate_json")
    
    if not candidate_json:
        st.info("📋 No profile data found. Please save a profile first in the **Profile** tab.")
        st.markdown("""
        This tab will use AI to analyze:
        - Your technical skills from resume, LinkedIn, and GitHub
        - Years of experience in different domains
        - Project expertise and research contributions
        - Suggested career roles based on your profile
        """)
        return
    
    # Cache analysis to avoid repeated API calls
    cache_key = f"skills_analysis_{hash(json.dumps(candidate_json, sort_keys=True))}"
    
    if cache_key not in st.session_state:
        with st.spinner("🤖 Analyzing your profile with AI..."):
            st.session_state[cache_key] = analyze_with_gemini(candidate_json)
    
    # Display analysis
    st.markdown(st.session_state[cache_key])
    
    # Add data sources footer
    st.divider()
    data_sources = candidate_json.get("data_sources", [])
    if data_sources:
        st.caption(f"📂 Analysis based on: {', '.join(data_sources).upper()}")
    
    # Refresh button
    if st.button("🔄 Regenerate Analysis"):
        del st.session_state[cache_key]
        st.rerun()
