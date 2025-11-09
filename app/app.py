import streamlit as st
from dotenv import load_dotenv
import os
import asyncio
import tempfile
import pandas as pd
from typing import List, Dict, Optional

# Try importing user's existing pipeline functions. If they don't exist in this environment,
# fallback to lightweight heuristics so the app still runs for demo purposes.
try:
    from aggregator import parse_all
except Exception:
    parse_all = None

try:
    from services.job_scraper.main_job import extract_job_search_queries
except Exception:
    # fallback extractor: build simple queries from candidate_json
    def extract_job_search_queries(candidate_json: dict) -> List[Dict]:
        keywords = []
        # Try to get top skill categories
        for sk in candidate_json.get("skills", [])[:3]:
            if isinstance(sk, dict):
                keywords.extend(sk.get("skills", [])[:2])
            elif isinstance(sk, str):
                keywords.append(sk)
        # fallback to headline
        if not keywords and candidate_json.get("contact_info", {}).get("headline"):
            keywords.append(candidate_json["contact_info"]["headline"])
        # build a small list of search params
        loc = candidate_json.get("contact_info", {}).get("location", "")
        # normalize experience using simple mapping
        experience = "Entry level"
        return [{"keyword": k, "location": loc or "India", "experience": experience} for k in keywords[:5]]

try:
    from services.job_scraper.job_scraper import scrape_linkedin_jobs
except Exception:
    scrape_linkedin_jobs = None

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
# Helper functions
# ---------------------------
def render_job_card(job: dict, query_idx: int, job_idx: int) -> str:
    title = job.get('title', 'Unknown Title')
    company = job.get('company', 'Unknown Company')
    location = job.get('location', 'Unknown Location')
    url = job.get('url', '#')
    desc = job.get('description', '') or ''
    skills = job.get('skills', []) or []

    # truncate description
    if len(desc) > 600:
        desc_short = desc[:600].rsplit(' ', 1)[0] + '...'
    else:
        desc_short = desc

    skill_html = ''.join([f"<span style='display:inline-block;padding:3px 8px;margin:2px;border-radius:12px;border:1px solid #ddd;font-size:12px'>{s}</span>" for s in skills])

    html = f"""
    <div style='border:1px solid #e6e6e6;border-radius:12px;padding:16px;margin-bottom:12px;box-shadow:0 2px 6px rgba(0,0,0,0.03)'>
      <div style='display:flex;justify-content:space-between;align-items:center'>
        <div style='max-width:75%'>
          <div style='font-weight:700;font-size:16px'>{title}</div>
          <div style='color:#555;margin-top:4px'>{company} • {location}</div>
        </div>
        <div style='text-align:right'>
          <a href='{url}' target='_blank' style='background:#0f62fe;color:#fff;padding:8px 12px;border-radius:8px;text-decoration:none;font-weight:600;margin-bottom:6px;display:inline-block'>Apply / Details</a>
        </div>
      </div>
      <div style='margin-top:12px;color:#333'>{desc_short}</div>
      <div style='margin-top:10px'>{skill_html}</div>
    </div>
    """
    return html

def run_parse_and_save(resume_bytes: Optional[bytes], linkedin_bytes: Optional[bytes], github_username: str):
    """Call parse_all if available, otherwise build a demo candidate_json. Store into session_state."""
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

def build_queries_and_run_scraper(pages:int, results_per_page:int, max_workers:int):
    """Build job queries and (optionally) run scraper per query. Saves job_results in session_state."""
    candidate_json = st.session_state.get("candidate_json") or {}
    try:
        queries = extract_job_search_queries(candidate_json)
    except Exception as e:
        st.warning("Extractor unavailable or failed; using fallback heuristics.")
        queries = extract_job_search_queries(candidate_json)
    st.session_state["job_queries"] = queries

    # Run scraper for each query if scraper exists. Otherwise leave placeholder empty DF.
    for i, q in enumerate(queries):
        if scrape_linkedin_jobs is None:
            df = pd.DataFrame(columns=["title", "company", "location", "url", "description", "skills"])
        else:
            try:
                df = scrape_linkedin_jobs(
                    keywords=q["keyword"],
                    location=q.get("location", ""),
                    experience=q.get("experience", ""),
                    pages=int(pages),
                    results_per_page=int(results_per_page),
                    max_workers=int(max_workers),
                    out_csv=None,
                )
            except Exception as e:
                st.error(f"Scraper error for query {q}: {e}")
                df = pd.DataFrame(columns=["title", "company", "location", "url", "description", "skills"])
        # normalize: ensure DataFrame
        if df is None:
            df = pd.DataFrame(columns=["title", "company", "location", "url", "description", "skills"])
        st.session_state["job_results"][i] = df

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
# PROFILE tab (upload + save)
# ---------------------------
if st.session_state["active_tab"] == "Profile":
    st.header("Profile — upload & save")
    col1, col2 = st.columns([2, 1])

    with col1:
        resume_file = st.file_uploader("Upload resume PDF", type=["pdf"], key="profile_resume")
        linkedin_file = st.file_uploader("Upload LinkedIn profile PDF", type=["pdf"], key="profile_linkedin")
        github_username = st.text_input("GitHub username (optional)", value=st.session_state.get("github_username", ""), key="profile_github")
        extra_notes = st.text_area("Optional notes (internal)", value="", help="Add any notes you want the parser to consider (dev-only)")

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
                run_parse_and_save(st.session_state["resume_bytes"], st.session_state["linkedin_bytes"], github_username)
            # clear old job queries/results because profile changed
            st.session_state["job_queries"] = []
            st.session_state["job_results"] = {}
            st.session_state["selected_job"] = None

# ---------------------------
# WHAT AM I GOOD AT? (placeholder)
# ---------------------------
elif st.session_state["active_tab"] == "What Am I good at?":
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

# ---------------------------
# JOB SEARCH tab: core functionality (scraper + cards)
# ---------------------------
elif st.session_state["active_tab"] == "Job Search":
    st.header("Job Search")
    if not st.session_state.get("candidate_json"):
        st.info("No saved profile. Go to the Profile tab and click Save Profile first.")
    else:
        st.write("Profile found. You can generate queries & run the scraper for the saved profile.")
        if st.button("Generate job queries & run scraper"):
            with st.spinner("Building queries and scraping..."):
                build_queries_and_run_scraper(pages, results_per_page, max_workers)
            st.success("Queries generated and scraper run (or demo placeholders created).")

        if not st.session_state.get("job_queries"):
            st.info("No job queries available. Click 'Generate job queries & run scraper' to produce queries.")
        else:
            queries = st.session_state["job_queries"]
            for i, q in enumerate(queries, start=1):
                st.markdown(f"---\n### Query {i}: **{q['keyword']}** — {q['location']} — {q['experience']}")
                df = st.session_state["job_results"].get(i-1, pd.DataFrame(columns=["title", "company", "location", "url", "description", "skills"]))
                if df is None or df.empty:
                    st.info("No results found for this query.")
                    continue

                # CSV download per query
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
                df.to_csv(tmp.name, index=False)
                with open(tmp.name, "rb") as f:
                    st.download_button(label=f"Download CSV for '{q['keyword']}'", data=f, file_name=os.path.basename(tmp.name))

                # Show up to first 20 results as cards with a separate 'Open Reach out' button
                rows_to_show = min(20, len(df))
                for idx in range(rows_to_show):
                    job = df.iloc[idx].to_dict()
                    html = render_job_card(job, i-1, idx)
                    st.markdown(html, unsafe_allow_html=True)
                    if st.button("Open Reach out (placeholder)", key=f"open_reach_{i-1}_{idx}"):
                        st.session_state["selected_job"] = {"query_index": i-1, "job_index": idx, "job": job}
                        st.session_state["active_tab"] = "Reach out"
                        st.experimental_rerun()

                # Dataframe expander
                with st.expander(f"Show table for query '{q['keyword']}' ({len(df)} results)"):
                    st.dataframe(df)

# ---------------------------
# REACH OUT tab: placeholder but linked to selected job
# ---------------------------
elif st.session_state["active_tab"] == "Reach out":
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
                    st.session_state["selected_job"] = {"query_index": 0, "job_index": 0, "job": df.iloc[0].to_dict()}
                    st.experimental_rerun()
    else:
        st.write("Selected job (dev placeholder):")
        st.json(selected["job"])
        st.markdown("**Placeholder for reach-out logic** — developer tasks:")
        st.write("- Use job posting URL to extract recruiter/contact names and LinkedIn profiles.")
        st.write("- Show recommended message templates, AB tests, and contact priority.")
        st.write("- Allow export of contact list as CSV or send messages via integrated channels (LinkedIn/email).")
        st.warning("This page currently does not fetch contacts. Implement recruiter extraction & auth flows in backend.")

# Footer
st.markdown("---")
st.caption("Notes: The app expects `parse_all`, `extract_job_search_queries`, and `scrape_linkedin_jobs` to be importable. If absent, fallback heuristics are used. Tabs 'What Am I good at?' and 'Reach out' are placeholders for developer logic.")
