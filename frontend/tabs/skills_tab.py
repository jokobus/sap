import streamlit as st
import json
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, RootModel
from typing import List, Optional, Union, Literal
import random

GITHUB = Literal["Github"]
LINKEDIN = Literal["LinkedIn"]
RESUME = Literal["Resume"]

class SkillsOutput(BaseModel):
    skill: str
    confidence: float
    rationale: Optional[str] = None
    source: Union[GITHUB, LINKEDIN, RESUME]

class SkillsList(RootModel[List[SkillsOutput]]):
    pass

load_dotenv()

SKILLS_ANALYSIS_PROMPT = """
                            You are an expert candidate skills analyst. Analyze the different sources of user: github, linkedin, and resume; and extract some unique key insights about their skills, experience, and expertise that are not usually written in Resume/CV but could be useful And for each skill also output the source.

                            You can give from any of the following types of skills: 
                            - Technical skills (programming, ML/AI, cloud, etc.)
                            - Soft skills (communication, teamwork, leadership, etc.)
                            - Creative skills (design, writing, music, art, etc.)
                            - Analytical skills (research, problem solving, critical thinking, etc.)
                            - Miscellaneous useful life skills (public speaking, time management, negotiation, etc.)

                            Output list of skills in JSON format as specified.

                            ## RESUME DATA:
                            {resume_json} 
                            ## LINKEDIN DATA:
                            {linkedin_json}
                            ## GITHUB DATA:
                            {github_json}               
                        """


def analyze_with_gemini(resume_json, linkedin_json, github_json) -> str:
    """Use Gemini to analyze candidate profile and generate skills analysis."""
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=SKILLS_ANALYSIS_PROMPT.format(resume_json=resume_json, linkedin_json=linkedin_json, github_json=github_json),
        config={
            "response_mime_type": "application/json",
            "response_schema": SkillsList,
        }
    )
    return response.text

def render_skills_tab1233():
    st.header("What Am I good at? 🤖")
    
    resume_json = st.session_state.get("resume_json")
    linkedin_json = st.session_state.get("linkedin_json")
    github_json = st.session_state.get("github_json")
    
    if not (resume_json or linkedin_json or github_json):
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
            st.session_state[cache_key] = analyze_with_gemini(resume_json, linkedin_json, github_json)
    
    # Parse Gemini response
    try:
        skills_list = SkillsList.model_validate_json(st.session_state[cache_key])
    except Exception:
        st.error("Failed to parse AI response.")
        return
    
    # Render skills as colored flex boxes
    st.markdown("<div style='display:flex;flex-wrap:wrap;border:20px;gap:20px;'>", unsafe_allow_html=True)
    for skill_obj in skills_list.root:
        skill = skill_obj.skill
        conf = int(skill_obj.confidence * 100)  # 0-100
        color = f"hsl({random.randint(0, 360)}, 70%, 80%)"  # pastel random color
        text_color = "black"
        tooltip = skill_obj.rationale or f"Confidence: {conf}%"

        st.markdown(f"""
        <div title="{tooltip}" style="
            background:{color};
            color:{text_color};
            padding:8px 12px;
            border-radius:12px;
            font-weight:600;
            display:inline-block;
            min-width:80px;
            text-align:center;
            box-shadow:0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            {skill} ({conf}%)
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add data sources footer
    st.divider()
    data_sources = candidate_json.get("data_sources", [])
    if data_sources:
        st.caption(f"📂 Analysis based on: {', '.join(data_sources).upper()}")

    # Refresh button
    if st.button("🔄 Regenerate Analysis"):
        del st.session_state[cache_key]
        st.rerun()

def render_skills_tab():
    st.header("What Am I good at? 🤖")
    
    resume_json = st.session_state.get("resume_json")
    linkedin_json = st.session_state.get("linkedin_json")
    github_json = st.session_state.get("github_json")
    
    if not (resume_json or linkedin_json or github_json):
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
    cache_key = f"skills_analysis_{hash(json.dumps({'resume': resume_json, 'linkedin': linkedin_json, 'github': github_json}, sort_keys=True))}"
    if cache_key not in st.session_state:
        with st.spinner("🤖 Analyzing your profile with AI..."):
            st.session_state[cache_key] = analyze_with_gemini(resume_json, linkedin_json, github_json)
    
    # Parse Gemini response
    try:
        skills_list = SkillsList.model_validate_json(st.session_state[cache_key])
    except Exception:
        st.error("Failed to parse AI response.")
        return
    
    # Render skills as colored flex boxes
    st.markdown("<div style='display:flex;flex-wrap:wrap;gap:16px;'>", unsafe_allow_html=True)
    for skill_obj in skills_list.root[:10]:
        skill = skill_obj.skill
        conf = int(skill_obj.confidence * 100)  # 0-100
        color = f"hsl({random.randint(0, 360)}, 70%, 80%)"  # pastel random color
        text_color = "black"
        tooltip = f"{skill_obj.rationale or 'No rationale'} | Source: {skill_obj.source}"

        st.markdown(f"""
        <div title="{tooltip}" style="
            background:{color};
            color:{text_color};
            padding:10px 14px;
            border-radius:14px;
            font-weight:600;
            display:inline-block;
            min-width:100px;
            text-align:center;
            box-shadow:0 3px 6px rgba(0,0,0,0.12);
            transition: transform 0.2s, box-shadow 0.2s;
            cursor:default;
        " onmouseover="this.style.transform='scale(1.08)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.2)';" 
           onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 3px 6px rgba(0,0,0,0.12)';">
            {skill} ({conf}%)
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Refresh button
    if st.button("🔄 Regenerate Analysis"):
        del st.session_state[cache_key]
        st.rerun()


if __name__ == "__main__":
    candidate_json = {'contact_info': {'name': 'Aarya Agarwal', 'email': 'aarya.agarwal6@gmail.com', 'phone': '+91 91678 88248', 'location': 'Mandi, Himachal Pradesh, India', 'headline': 'Student at Indian Institute of Technology, Mandi', 'summary': None}, 'social_links': {'linkedin': 'https://linkedin.com/in/dnfy', 'github': 'https://github.com/dnfy502', 'portfolio': None, 'other_links': ['https://www.linkedin.com/in/dnfy?jobid=1234&lipi=urn%3Ali%3Apage%3Ad_jobs_easyapply_pdfgenresume%3BawGAl98USlWIsJ%2FDSrZSRg%3D%3D&licu=urn%3Ali%3Acontrol%3Ad_jobs_easyapply_pdfgenresume-v02_profile', 'mailto:aarya.agarwal6@gmail.com']}, 'education': [{'institute': 'Indian Institute of Technology, Mandi', 'degree': 'B.Tech in Computer Science & Engineering', 'field_of_study': 'Computer Engineering', 'start_year': 2023, 'end_year': 'Present', 'start_date_raw': None, 'end_date_raw': None, 'grade_info': {'value': 9.59, 'type': 'CGPA', 'scale': 10, 'description': None}, 'description': None, 'source': ['resume', 'linkedin']}, {'institute': 'Indian Institute of Technology, Madras', 'degree': 'Bachelor of Science', 'field_of_study': 'Data Science', 'start_year': 2023, 'end_year': 'Present', 'start_date_raw': None, 'end_date_raw': None, 'grade_info': {'value': 9.75, 'type': 'CGPA', 'scale': 10, 'description': None}, 'description': None, 'source': ['resume', 'linkedin']}, {'institute': 'Chennai Public School', 'degree': None, 'field_of_study': 'CBSE Class 12', 'start_year': 2021, 'end_year': 2023, 'start_date_raw': None, 'end_date_raw': None, 'grade_info': {'value': 97.8, 'type': 'PERCENTAGE', 'scale': 100, 'description': 'School Rank 1'}, 'description': None, 'source': ['resume', 'linkedin']}, {'institute': 'Chennai Public School - India', 'degree': '12th Grade', 'field_of_study': 'PCM', 'start_year': 2021, 'end_year': 2023, 'start_date_raw': None, 'end_date_raw': None, 'grade_info': None, 'description': None, 'source': ['linkedin']}], 'experience': [{'company': 'TradeVed', 'title': 'Software Engineer Intern', 'start_year': 2025, 'end_year': 'Present', 'start_date_raw': None, 'end_date_raw': None, 'duration_raw': None, 'location': None, 'description_points': ['Built a no-code Market Screener and Strategy Backtester for users with NextJS, React frontend', 'Deployed backend with PostgreSQL database for 320+ screening criteria, with sub-20ms query responses for 2000+ companies', 'Reduced API calls by 60% through multi-process data streaming pipeline with Redis caching, processing 550K+ daily datapoints'], 'source': ['resume']}, {'company': 'Anubhav Fellowship - IIT Mandi', 'title': 'Research Intern, CAIR Lab', 'start_year': 2025, 'end_year': 2025, 'start_date_raw': None, 'end_date_raw': None, 'duration_raw': None, 'location': None, 'description_points': ['Developed smart wheelchair navigation system using YOLO object detection with Intel RealSense depth camera', 'Implemented novel pipeline for reliable obstacle avoidance using object type and velocity with STVL in ROS'], 'source': ['resume']}], 'projects': [{'name': 'Brain Computer Interface Model', 'description_points': ['Engineered a SOTA EEG brain scan to image conversion model using novel LSTM+GAN depth pipeline', 'Increased depth dataset size by 16K EEG-image pairs (4x increase) through K-means clustering on image CLIP embeddings', 'Achieved 40% performance improvement on specific classes and 22% average improvement over year-old models'], 'link': 'https://github.com/Voldemort271/eeg-to-img.git', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['resume']}, {'name': 'NASA SpaceApps Challenge (Global Finalist)', 'description_points': ['Team Leader, Top 40 globally among 940+ teams, Top 2 in India, collaborated with 5 accomplished members', 'Developed an ML-driven web platform to visualize and predict CO2/CH4 emissions based on satellite and land-use data, providing grounded recommendations to policymakers through natural language', 'Trained Random Forest and SVM models (0.92 r2 score) using 200K+ datapoints scraped from NASA datasets'], 'link': 'https://github.com/Vinamra-21/Nasa-Spaceapps-Challenge', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['resume']}, {'name': 'Algorithmic Trading Systems', 'description_points': ['Deployed scalable backtesting and live trading systems with user portfolios worth Rs. 10 Lakh on MS Azure', 'Achieved 10x faster strategy tuning using Optuna, extended popular professional engines for multi-company backtesting', 'Created sub-5 min delay Market News service with advanced company analysis using Gemini with Search'], 'link': 'https://github.com/dnfy502/market-news-mail', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['resume']}, {'name': 'backtest', 'description_points': ['Backtesting backend files'], 'link': 'https://github.com/dnfy502/backtest', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'container_vulnerability', 'description_points': ['Security Expert Agent for Docker Containers'], 'link': 'https://github.com/dnfy502/container_vulnerability', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'data-updation-tradeVed', 'description_points': ['This is a screener developed for my internship in TradeVed.'], 'link': 'https://github.com/dnfy502/data-updation-tradeVed', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'isl_assignment1', 'description_points': ['The files and code for our data analysis project in ISL'], 'link': 'https://github.com/dnfy502/isl_assignment1', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'isl_assignment3', 'description_points': ['Assignment 3 for ISL woooooooooooooo'], 'link': 'https://github.com/dnfy502/isl_assignment3', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'market-news-mail', 'description_points': ['NSE market news tool that sends an email whenever any company reports a new order (with some extra useful information!)'], 'link': 'https://github.com/dnfy502/market-news-mail', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'online-judge', 'description_points': ['Project under Algo University'], 'link': 'https://github.com/dnfy502/online-judge', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'quantInsti-hackathon', 'description_points': [], 'link': 'https://github.com/dnfy502/quantInsti-hackathon', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'res_reader', 'description_points': ['I just wanna be able to read research papers easily man'], 'link': 'https://github.com/dnfy502/res_reader', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'screener-testing', 'description_points': [], 'link': 'https://github.com/dnfy502/screener-testing', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'sodor-cache', 'description_points': ['Added a 4 way associated L1 cache and 2 way associated L2 cache to the education sodor chip in chipyard (scala)'], 'link': 'https://github.com/dnfy502/sodor-cache', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'soundfiles', 'description_points': ['Repo to store code for converting sound files from different formats, and some 2-3 ways to clean background noise.'], 'link': 'https://github.com/dnfy502/soundfiles', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'traffic_analysis', 'description_points': ['Our mongodb collection is called bingus bongus. God help us all.'], 'link': 'https://github.com/dnfy502/traffic_analysis', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'urc-rock-detection-24', 'description_points': ['Rock detection dataset and trained YOLOv8neo model '], 'link': 'https://github.com/dnfy502/urc-rock-detection-24', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'zelta-architect', 'description_points': ['Zelta architect hackathon files'], 'link': 'https://github.com/dnfy502/zelta-architect', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}], 'skills': [{'category_name': 'Languages', 'skills': ['Python', 'C++', 'JavaScript', 'SQL', 'MongoDB', 'Scala', 'Matlab'], 'source': ['resume']}, {'category_name': 'Frameworks & Tools', 'skills': ['Git', 'Docker', 'Postman', 'Microsoft Azure', 'AWS', 'Django', 'FastAPI', 'Linux Shell'], 'source': ['resume']}, {'category_name': 'Specializations', 'skills': ['Machine Learning', 'System Design', 'Backend Development', 'Data Structures and Algorithms'], 'source': ['resume']}, {'category_name': 'Programming Languages (from GitHub)', 'skills': ['Jupyter Notebook', 'HTML', 'TypeScript', 'Shell', 'CSS', 'CMake', 'Dockerfile', 'Procfile'], 'source': ['github']}, {'category_name': 'Top Skills', 'skills': ['GitHub', 'Greenhouse Gas', 'Intermediary'], 'source': ['linkedin']}], 'certifications': [], 'achievements': ['All India Rank 52 (ISI Kolkata B.Stat) and 41XX (JEE Advanced 2023)', 'Awarded 2.5 Lakh grant with runner up in institutional startup program for pioneering modular medical solutions'], 'positions_of_responsibility': [{'title': 'President of Debating Club', 'organization': 'IIT Mandi', 'start_year': 2023, 'end_year': 'Present', 'start_date_raw': None, 'end_date_raw': None, 'description_points': ['Lead team of 10+ people', 'Held debate events with 60+ turnout'], 'source': ['resume']}], 'courses': [], 'data_sources': ['resume', 'linkedin', 'github'], 'last_updated': None}
    resume_json = {'name': 'Aarya Agarwal', 'email': 'aarya.agarwal6@gmail.com', 'phone': '+91 91678 88248', 'social_links': ['https://linkedin.com/in/dnfy', 'https://github.com/dnfy502'], 'courses': [], 'education': [{'institute': 'Indian Institute of Technology, Mandi', 'field_of_study': 'B.Tech in Computer Science & Engineering', 'start_year': 2023, 'end_year': 'Present', 'grade_info': {'value': 9.59, 'type': 'CGPA', 'scale': 10, 'description': None}}, {'institute': 'Indian Institute of Technology, Madras', 'field_of_study': 'B.Sc in Data Science (Dual Degree Program)', 'start_year': 2023, 'end_year': 'Present', 'grade_info': {'value': 9.75, 'type': 'CGPA', 'scale': 10, 'description': None}}, {'institute': 'Chennai Public School', 'field_of_study': 'CBSE Class 12', 'start_year': 2021, 'end_year': 2023, 'grade_info': {'value': 97.8, 'type': 'PERCENTAGE', 'scale': 100, 'description': None}}], 'experience': [{'title': 'Software Engineer Intern', 'company': 'TradeVed', 'start_year': 2025, 'end_year': 'Present', 'description_points': ['Built a no-code Market Screener and Strategy Backtester for users with NextJS, React frontend', 'Deployed backend with PostgreSQL database for 320+ screening criteria, with sub-20ms query responses for 2000+ companies', 'Reduced API calls by 60% through multi-process data streaming pipeline with Redis caching, processing 550K+ daily datapoints']}, {'title': 'Research Intern, CAIR Lab', 'company': 'Anubhav Fellowship - IIT Mandi', 'start_year': 2025, 'end_year': 2025, 'description_points': ['Developed smart wheelchair navigation system using YOLO object detection with Intel RealSense depth camera', 'Implemented novel pipeline for reliable obstacle avoidance using object type and velocity with STVL in ROS']}], 'projects': [{'name': 'Brain Computer Interface Model', 'description_points': ['Engineered a SOTA EEG brain scan to image conversion model using novel LSTM+GAN depth pipeline', 'Increased depth dataset size by 16K EEG-image pairs (4x increase) through K-means clustering on image CLIP embeddings', 'Achieved 40% performance improvement on specific classes and 22% average improvement over year-old models'], 'link': 'https://github.com/Voldemort271/eeg-to-img.git'}, {'name': 'NASA SpaceApps Challenge (Global Finalist)', 'description_points': ['Team Leader, Top 40 globally among 940+ teams, Top 2 in India, collaborated with 5 accomplished members', 'Developed an ML-driven web platform to visualize and predict CO2/CH4 emissions based on satellite and land-use data, providing grounded recommendations to policymakers through natural language', 'Trained Random Forest and SVM models (0.92 r2 score) using 200K+ datapoints scraped from NASA datasets'], 'link': 'https://github.com/Vinamra-21/Nasa-Spaceapps-Challenge'}, {'name': 'Algorithmic Trading Systems', 'description_points': ['Deployed scalable backtesting and live trading systems with user portfolios worth Rs. 10 Lakh on MS Azure', 'Achieved 10x faster strategy tuning using Optuna, extended popular professional engines for multi-company backtesting', 'Created sub-5 min delay Market News service with advanced company analysis using Gemini with Search'], 'link': 'https://github.com/dnfy502/market-news-mail'}], 'skills': [{'category_name': 'Languages', 'skills': ['Python', 'C++', 'JavaScript', 'SQL', 'MongoDB', 'Scala', 'Matlab']}, {'category_name': 'Frameworks & Tools', 'skills': ['Git', 'Docker', 'Postman', 'Microsoft Azure', 'AWS', 'Django', 'FastAPI', 'Linux Shell']}, {'category_name': 'Specializations', 'skills': ['Machine Learning', 'System Design', 'Backend Development', 'Data Structures and Algorithms']}], 'certifications': [], 'achievements': ['All India Rank 52 (ISI Kolkata B.Stat) and 41XX (JEE Advanced 2023)', 'Awarded 2.5 Lakh grant with runner up in institutional startup program for pioneering modular medical solutions'], 'positions_of_responsibility': [{'title': 'President of Debating Club', 'organization': 'IIT Mandi', 'start_year': 2024, 'end_year': 'Present', 'description_points': ['Lead team of 10+ people', 'Held debate events with 60+ turnout']}]}
    linkedin_json = {'name': 'Aarya Agarwal', 'headline': 'Student at Indian Institute of Technology, Mandi', 'location': 'Mandi, Himachal Pradesh, India', 'contact': {'email': 'aarya.agarwal6@gmail.com', 'phone': None, 'address': None, 'profile_url': 'https://www.linkedin.com/in/dnfy', 'other_links': ['https://www.linkedin.com/in/dnfy?jobid=1234&lipi=urn%3Ali%3Apage%3Ad_jobs_easyapply_pdfgenresume%3BawGAl98USlWIsJ%2FDSrZSRg%3D%3D&licu=urn%3Ali%3Acontrol%3Ad_jobs_easyapply_pdfgenresume-v02_profile', 'mailto:aarya.agarwal6@gmail.com']}, 'about': None, 'top_skills': ['GitHub', 'Greenhouse Gas', 'Intermediary'], 'honors_awards': [], 'certifications': [], 'experience': [], 'education': [{'institute': 'Indian Institute of Technology, Mandi', 'degree': 'Bachelor of Technology', 'field_of_study': 'Computer Engineering', 'start_year': 2023, 'end_year': 2027, 'grade_info': None}, {'institute': 'Chennai Public School', 'degree': None, 'field_of_study': None, 'start_year': 2021, 'end_year': 2023, 'grade_info': None}, {'institute': 'Chennai Public School', 'degree': None, 'field_of_study': None, 'start_year': 2021, 'end_year': 2023, 'grade_info': None}, {'institute': 'Chennai Public School - India', 'degree': '12th Grade', 'field_of_study': 'PCM', 'start_year': 2021, 'end_year': 2023, 'grade_info': None}, {'institute': 'Indian Institute of Technology, Madras', 'degree': 'Bachelor of Science', 'field_of_study': 'Data Science', 'start_year': 2023, 'end_year': None, 'grade_info': None}], 'projects': [], 'publications': [], 'volunteer_experience': [], 'courses': [], 'languages': [], 'recommendations_count': None}
    github_json = {
  "projects": [
    {
      "name": "backtest",
      "description_points": [
        "Backtesting backend files"
      ],
      "link": "https://github.com/dnfy502/backtest"
    },
    {
      "name": "container_vulnerability",
      "description_points": [
        "Security Expert Agent for Docker Containers"
      ],
      "link": "https://github.com/dnfy502/container_vulnerability"
    },
    {
      "name": "data-updation-tradeVed",
      "description_points": [
        "This is a screener developed for my internship in TradeVed."
      ],
      "link": "https://github.com/dnfy502/data-updation-tradeVed"
    },
    {
      "name": "isl_assignment1",
      "description_points": [
        "The files and code for our data analysis project in ISL"
      ],
      "link": "https://github.com/dnfy502/isl_assignment1"
    },
    {
      "name": "isl_assignment3",
      "description_points": [
        "Assignment 3 for ISL woooooooooooooo"
      ],
      "link": "https://github.com/dnfy502/isl_assignment3"
    },
    {
      "name": "market-news-mail",
      "description_points": [
        "NSE market news tool that sends an email whenever any company reports a new order (with some extra useful information!)"
      ],
      "link": "https://github.com/dnfy502/market-news-mail"
    },
    {
      "name": "online-judge",
      "description_points": [
        "Project under Algo University"
      ],
      "link": "https://github.com/dnfy502/online-judge"
    },
    {
      "name": "quantInsti-hackathon",
      "description_points": [],
      "link": "https://github.com/dnfy502/quantInsti-hackathon"
    },
    {
      "name": "res_reader",
      "description_points": [
        "I just wanna be able to read research papers easily man"
      ],
      "link": "https://github.com/dnfy502/res_reader"
    },
    {
      "name": "screener-testing",
      "description_points": [],
      "link": "https://github.com/dnfy502/screener-testing"
    },
    {
      "name": "sodor-cache",
      "description_points": [
        "Added a 4 way associated L1 cache and 2 way associated L2 cache to the education sodor chip in chipyard (scala)"
      ],
      "link": "https://github.com/dnfy502/sodor-cache"
    },
    {
      "name": "soundfiles",
      "description_points": [
        "Repo to store code for converting sound files from different formats, and some 2-3 ways to clean background noise."
      ],
      "link": "https://github.com/dnfy502/soundfiles"
    },
    {
      "name": "traffic_analysis",
      "description_points": [
        "Our mongodb collection is called bingus bongus. God help us all."
      ],
      "link": "https://github.com/dnfy502/traffic_analysis"
    },
    {
      "name": "urc-rock-detection-24",
      "description_points": [
        "Rock detection dataset and trained YOLOv8neo model "
      ],
      "link": "https://github.com/dnfy502/urc-rock-detection-24"
    },
    {
      "name": "zelta-architect",
      "description_points": [
        "Zelta architect hackathon files"
      ],
      "link": "https://github.com/dnfy502/zelta-architect"
    }
  ],
  "skills": [
    {
      "category_name": "Programming Languages (from GitHub)",
      "skills": [
        "Jupyter Notebook",
        "Python",
        "HTML",
        "TypeScript",
        "Scala",
        "Shell",
        "JavaScript",
        "CSS",
        "CMake",
        "Dockerfile",
        "Procfile"
      ]
    }
  ],
  "social_links": [
    "https://github.com/dnfy502"
  ]
}
    print(analyze_with_gemini(resume_json, linkedin_json, github_json))
