import os
from dotenv import load_dotenv

# Use google-generativeai (AI Studio) instead of deprecated google.genai
try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except ImportError:
    genai = None  # type: ignore
    _GENAI_AVAILABLE = False

# Structured output types (optional). If not available, we'll fallback to plain JSON parsing.
try:
    from google.generativeai import types as genai_types  # type: ignore
except Exception:
    genai_types = None
from services.job_scraper.job_schema import JobSearchList, JobSearchParams
from typing import List

# Optional/demo imports (not required for extract_job_search_queries). Guard them.
try:
    from app.aggregator import parse_all  # type: ignore
except Exception:
    parse_all = None  # type: ignore
try:
    from services.job_scraper.job_scraper import scrape_linkedin_jobs  # type: ignore
except Exception:
    scrape_linkedin_jobs = None  # type: ignore
import asyncio

load_dotenv()

# Configure model lazily within function to avoid failing at import-time
MODEL = "gemini-2.0-flash"

PROMPT = """
            You are a job search assistant. Given the candidate's parsed profile JSON below, extract a structured list of job search parameters.
            Each item must be a JSON object with these keys:
            - "keyword": string (job role or skills; eg: machine learning engineer)
            - "location": string (country name only)
            - "experience": string (like 'Internship', 'Entry level', 'Associate', 'Mid-Senior level')

            Input JSON:
            {candidate_json}
        """

def extract_job_search_queries(candidate_json: dict) -> list[JobSearchParams]:
    if not _GENAI_AVAILABLE:
        raise RuntimeError("google-generativeai is not installed. Install with `pip install google-generativeai`.")

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY (or GEMINI_API_KEY) environment variable.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODEL)

    prompt = PROMPT.format(candidate_json=candidate_json)

    # Prefer structured response if supported; otherwise parse JSON from text
    if genai_types and hasattr(genai_types, "GenerateContentConfig"):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai_types.GenerationConfig(response_mime_type="application/json"),
            )
            return JobSearchList.model_validate_json(response.text).model_dump()
        except Exception:
            # fallback to plain text JSON parsing
            pass

    # Fallback: ask for strict JSON and parse
    json_prompt = (
        "Return ONLY valid JSON array (no commentary) matching the schema: "
        "[{\"keyword\": string, \"location\": string, \"experience\": string}]\n\n"
        + prompt
    )
    response = model.generate_content(json_prompt)

    import json as _json
    try:
        data = _json.loads(response.text)
    except Exception:
        # Try to extract JSON block heuristically
        import re
        m = re.search(r"\[.*\]", response.text, re.S)
        if not m:
            raise RuntimeError("Model did not return JSON for job search queries.")
        data = _json.loads(m.group(0))

    # Validate and coerce using Pydantic schema
    try:
        return JobSearchList.model_validate(data).model_dump()
    except Exception as e:
        raise RuntimeError(f"Invalid job query JSON: {e}")



# Example: get candidate JSON
resume_bytes = open("aarya.pdf", "rb").read()
linkedin_bytes = open("pro.pdf", "rb").read()
github_username = "dnfy502"

# candidate_json = asyncio.run(parse_all(resume_bytes, linkedin_bytes, github_username))
# candidate_json = {'contact_info': {'name': 'Aarya Agarwal', 'email': 'aarya.agarwal6@gmail.com', 'phone': '+91 91678 88248', 'location': 'Mandi, Himachal Pradesh, India', 'headline': 'Student at Indian Institute of Technology, Mandi', 'summary': None}, 'social_links': {'linkedin': 'https://linkedin.com/in/dnfy', 'github': 'https://github.com/dnfy502', 'portfolio': None, 'other_links': ['https://www.linkedin.com/in/dnfy?jobid=1234&lipi=urn%3Ali%3Apage%3Ad_jobs_easyapply_pdfgenresume%3BawGAl98USlWIsJ%2FDSrZSRg%3D%3D&licu=urn%3Ali%3Acontrol%3Ad_jobs_easyapply_pdfgenresume-v02_profile', 'mailto:aarya.agarwal6@gmail.com']}, 'education': [{'institute': 'Indian Institute of Technology, Mandi', 'degree': 'Bachelor of Technology', 'field_of_study': 'B.Tech in Computer Science & Engineering', 'start_year': 2023, 'end_year': 'Present', 'start_date_raw': None, 'end_date_raw': None, 'grade_info': {'value': 9.59, 'type': 'CGPA', 'scale': 10, 'description': None}, 'description': None, 'source': ['resume', 'linkedin']}, {'institute': 'Indian Institute of Technology, Madras', 'degree': 'Bachelor of Science', 'field_of_study': 'Data Science', 'start_year': 2023, 'end_year': 'Present', 'start_date_raw': None, 'end_date_raw': None, 'grade_info': {'value': 9.75, 'type': 'CGPA', 'scale': 10, 'description': None}, 'description': None, 'source': ['resume', 'linkedin']}, {'institute': 'Chennai Public School', 'degree': None, 'field_of_study': 'CBSE Class 12', 'start_year': 2021, 'end_year': 2023, 'start_date_raw': None, 'end_date_raw': None, 'grade_info': {'value': 97.8, 'type': 'PERCENTAGE', 'scale': 100, 'description': None}, 'description': None, 'source': ['resume', 'linkedin']}, {'institute': 'Chennai Public School - India', 'degree': '12th Grade', 'field_of_study': 'PCM', 'start_year': 2021, 'end_year': 2023, 'start_date_raw': None, 'end_date_raw': None, 'grade_info': None, 'description': None, 'source': ['linkedin']}], 'experience': [{'company': 'TradeVed', 'title': 'Software Engineer Intern', 'start_year': 2025, 'end_year': 'Present', 'start_date_raw': None, 'end_date_raw': None, 'duration_raw': None, 'location': None, 'description_points': ['Built a no-code Market Screener and Strategy Backtester for users with NextJS, React frontend', 'Deployed backend with PostgreSQL database for 320+ screening criteria, with sub-20ms query responses for 2000+ companies', 'Reduced API calls by 60% through multi-process data streaming pipeline with Redis caching, processing 550K+ daily datapoints'], 'source': ['resume']}, {'company': 'Anubhav Fellowship - IIT Mandi', 'title': 'Research Intern, CAIR Lab', 'start_year': 2025, 'end_year': 2025, 'start_date_raw': None, 'end_date_raw': None, 'duration_raw': None, 'location': None, 'description_points': ['Developed smart wheelchair navigation system using YOLO object detection with Intel RealSense depth camera', 'Implemented novel pipeline for reliable obstacle avoidance using object type and velocity with STVL in ROS'], 'source': ['resume']}], 'projects': [{'name': 'Brain Computer Interface Model', 'description_points': ['Engineered a SOTA EEG brain scan to image conversion model using novel LSTM+GAN depth pipeline', 'Increased depth dataset size by 16K EEG-image pairs (4x increase) through K-means clustering on image CLIP embeddings', 'Achieved 40% performance improvement on specific classes and 22% average improvement over year-old models'], 'link': 'https://github.com/Voldemort271/eeg-to-img.git', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['resume']}, {'name': 'NASA SpaceApps Challenge (Global Finalist)', 'description_points': ['Team Leader, Top 40 globally among 940+ teams, Top 2 in India, collaborated with 5 accomplished members', 'Developed an ML-driven web platform to visualize and predict CO2/CH4 emissions based on satellite and land-use data, providing grounded recommendations to policymakers through natural language', 'Trained Random Forest and SVM models (0.92 r2 score) using 200K+ datapoints scraped from NASA datasets'], 'link': 'https://github.com/Vinamra-21/Nasa-Spaceapps-Challenge', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['resume']}, {'name': 'Algorithmic Trading Systems', 'description_points': ['Deployed scalable backtesting and live trading systems with user portfolios worth Rs. 10 Lakh on MS Azure', 'Achieved 10x faster strategy tuning using Optuna, extended popular professional engines for multi-company backtesting', 'Created sub-5 min delay Market News service with advanced company analysis using Gemini with Search'], 'link': 'https://github.com/dnfy502/market-news-mail', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['resume']}, {'name': 'backtest', 'description_points': ['Backtesting backend files'], 'link': 'https://github.com/dnfy502/backtest', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'container_vulnerability', 'description_points': ['Security Expert Agent for Docker Containers'], 'link': 'https://github.com/dnfy502/container_vulnerability', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'data-updation-tradeVed', 'description_points': ['This is a screener developed for my internship in TradeVed.'], 'link': 'https://github.com/dnfy502/data-updation-tradeVed', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'isl_assignment1', 'description_points': ['The files and code for our data analysis project in ISL'], 'link': 'https://github.com/dnfy502/isl_assignment1', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'isl_assignment3', 'description_points': ['Assignment 3 for ISL woooooooooooooo'], 'link': 'https://github.com/dnfy502/isl_assignment3', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'market-news-mail', 'description_points': ['NSE market news tool that sends an email whenever any company reports a new order (with some extra useful information!)'], 'link': 'https://github.com/dnfy502/market-news-mail', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'online-judge', 'description_points': ['Project under Algo University'], 'link': 'https://github.com/dnfy502/online-judge', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'quantInsti-hackathon', 'description_points': [], 'link': 'https://github.com/dnfy502/quantInsti-hackathon', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'res_reader', 'description_points': ['I just wanna be able to read research papers easily man'], 'link': 'https://github.com/dnfy502/res_reader', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'screener-testing', 'description_points': [], 'link': 'https://github.com/dnfy502/screener-testing', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'sodor-cache', 'description_points': ['Added a 4 way associated L1 cache and 2 way associated L2 cache to the education sodor chip in chipyard (scala)'], 'link': 'https://github.com/dnfy502/sodor-cache', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'soundfiles', 'description_points': ['Repo to store code for converting sound files from different formats, and some 2-3 ways to clean background noise.'], 'link': 'https://github.com/dnfy502/soundfiles', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'traffic_analysis', 'description_points': ['Our mongodb collection is called bingus bongus. God help us all.'], 'link': 'https://github.com/dnfy502/traffic_analysis', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'urc-rock-detection-24', 'description_points': ['Rock detection dataset and trained YOLOv8neo model '], 'link': 'https://github.com/dnfy502/urc-rock-detection-24', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}, {'name': 'zelta-architect', 'description_points': ['Zelta architect hackathon files'], 'link': 'https://github.com/dnfy502/zelta-architect', 'start_date_raw': None, 'end_date_raw': None, 'associated_with': None, 'technologies': [], 'github_stars': None, 'github_forks': None, 'is_github_repo': False, 'source': ['github']}], 'skills': [{'category_name': 'Languages', 'skills': ['Python', 'C++', 'JavaScript', 'SQL', 'MongoDB', 'Scala', 'Matlab'], 'source': ['resume']}, {'category_name': 'Frameworks & Tools', 'skills': ['Git', 'Docker', 'Postman', 'Microsoft Azure', 'AWS', 'Django', 'FastAPI', 'Linux Shell'], 'source': ['resume']}, {'category_name': 'Specializations', 'skills': ['Machine Learning', 'System Design', 'Backend Development', 'Data Structures and Algorithms'], 'source': ['resume']}, {'category_name': 'Programming Languages (from GitHub)', 'skills': ['Jupyter Notebook', 'Python', 'HTML', 'TypeScript', 'Scala', 'Shell', 'JavaScript', 'CSS', 'CMake', 'Dockerfile', 'Procfile'], 'source': ['github']}, {'category_name': 'Top Skills', 'skills': ['GitHub', 'Greenhouse Gas', 'Intermediary'], 'source': ['linkedin']}], 'certifications': [], 'achievements': ['All India Rank 52 (ISI Kolkata B.Stat) and 41XX (JEE Advanced 2023)', 'Awarded 2.5 Lakh grant with runner up in institutional startup program for pioneering modular medical solutions'], 'positions_of_responsibility': [{'title': 'President', 'organization': 'Debating Club, IIT Mandi', 'start_year': 2024, 'end_year': 'Present', 'start_date_raw': None, 'end_date_raw': None, 'description_points': ['Lead team of 10+ people', 'Held debate events with 60+ turnout'], 'source': ['resume']}], 'courses': [], 'data_sources': ['resume', 'linkedin', 'github'], 'last_updated': None} 

# Convert to list of job search queries
# job_queries = extract_job_search_queries(candidate_json)


# print(f"Job queries: {job_queries}")
# for query in job_queries:
#     df = scrape_linkedin_jobs(
#         keywords=query["keyword"],
#         location=query["location"],
#         experience=query["experience"],  # Enum already serialized as string by RootModel
#         pages=2,
#         results_per_page=5,
#         max_workers=4,
#         out_csv=f"jobs_{query['keyword']}_{query['location']}.csv"
#     )
#     print(df.head())
#     print(f"Scraped {len(df)} jobs for query: {query}\n")
