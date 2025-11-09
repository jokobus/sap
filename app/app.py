import streamlit as st
from dotenv import load_dotenv
import os
import tempfile
import pandas as pd
import json
from typing import Optional

# ---------------------------
# Import modular functions (implement these in separate files under services/ or utils/)
# ---------------------------
try:
    from services.parser import run_parse_and_save
except Exception:
    run_parse_and_save = None

try:
    from services.scraper import build_queries_and_run_scraper
except Exception:
    build_queries_and_run_scraper = None

try:
    from services.ranking import collect_and_dedupe_jobs, rank_jobs
except Exception:
    collect_and_dedupe_jobs = None
    rank_jobs = None

try:
    from ui_helpers import render_job_card, render_job_card_with_score
except Exception:
    render_job_card = None
    render_job_card_with_score = None

# ---------------------------
# Streamlit page config + session state
# ---------------------------
st.set_page_config(page_title="Modular Job Finder", layout="wide")
load_dotenv()

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
if "collected_jobs" not in st.session_state:
    st.session_state["collected_jobs"] = []
if "ranked_jobs" not in st.session_state:
    st.session_state["ranked_jobs"] = []
if "selected_job" not in st.session_state:
    st.session_state["selected_job"] = None
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Profile"

# ---------------------------
# Sidebar: tabs and global controls
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
st.title("Job Finder — Modular UI")
st.write("Profile-driven job discovery. UI logic is separated from business logic in services/ and ui_helpers.")

# ---------------------------
# PROFILE tab: upload + save
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
            if run_parse_and_save is None:
                st.error("Parser module not found. Implement services.parser.run_parse_and_save to enable parsing.")
            else:
                with st.spinner("Parsing candidate profile..."):
                    # parse_and_save should accept (resume_bytes, linkedin_bytes, github_username) and return candidate_json
                    candidate_json = run_parse_and_save(st.session_state["resume_bytes"], st.session_state["linkedin_bytes"], github_username)
                    st.session_state["candidate_json"] = candidate_json
                    # clear downstream caches
                    st.session_state["job_queries"] = []
                    st.session_state["job_results"] = {}
                    st.session_state["collected_jobs"] = []
                    st.session_state["ranked_jobs"] = []
                    st.success("Profile saved.")

# ---------------------------
# WHAT AM I GOOD AT? (placeholder)
# ---------------------------
elif st.session_state["active_tab"] == "What Am I good at?":
    st.header("What Am I good at?")
    st.info("Placeholder: analysis logic should live in services.analysis (not implemented here).")
    candidate_json = st.session_state.get("candidate_json") or {}
    skills = candidate_json.get("skills", [])
    if skills:
        st.write("Detected skills (raw):")
        st.write(skills)
    else:
        st.info("No skills detected. Save a profile first in the Profile tab.")

# ---------------------------
# JOB SEARCH tab: uses scraper module to generate queries and results
# ---------------------------
elif st.session_state["active_tab"] == "Job Search":
    st.header("Job Search")
    if not st.session_state.get("candidate_json"):
        st.info("No saved profile. Go to the Profile tab and click Save Profile first.")
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Generate job queries & run scraper"):
                if build_queries_and_run_scraper is None:
                    st.error("Scraper module not found. Implement services.scraper.build_queries_and_run_scraper to enable scraping.")
                else:
                    with st.spinner("Building queries and scraping..."):
                        queries, results = build_queries_and_run_scraper(st.session_state["candidate_json"], pages, results_per_page, max_workers)
                        # build_queries_and_run_scraper should return (queries_list, dict(query_index->DataFrame))
                        st.session_state["job_queries"] = queries
                        st.session_state["job_results"] = results
                        st.success("Queries generated and scraper run.")

        # show per-query results (if any)
        if not st.session_state.get("job_queries"):
            st.info("No job queries available. Generate queries first.")
        else:
            for i, q in enumerate(st.session_state["job_queries"], start=1):
                st.markdown(f"---\n### Query {i}: **{q['keyword']}** — {q['location']} — {q['experience']}")
                df = st.session_state["job_results"].get(i-1, pd.DataFrame(columns=["title", "company", "location", "url", "description", "skills"]))
                if df is None or df.empty:
                    st.info("No results found for this query.")
                    continue

                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
                df.to_csv(tmp.name, index=False)
                with open(tmp.name, "rb") as f:
                    st.download_button(label=f"Download CSV for '{q['keyword']}'", data=f, file_name=os.path.basename(tmp.name))

                rows_to_show = min(20, len(df))
                for idx in range(rows_to_show):
                    job = df.iloc[idx].to_dict()
                    if render_job_card is None:
                        st.write(job)
                    else:
                        st.markdown(render_job_card(job), unsafe_allow_html=True)
                    if st.button("Open Reach out", key=f"open_reach_{i-1}_{idx}"):
                        st.session_state["selected_job"] = {"query_index": i-1, "job_index": idx, "job": job}
                        st.session_state["active_tab"] = "Reach out"
                        st.experimental_rerun()

# ---------------------------
# REACH OUT tab: placeholder
# ---------------------------
elif st.session_state["active_tab"] == "Reach out":
    st.header("Reach out")
    selected = st.session_state.get("selected_job")
    if not selected:
        st.info("No job selected. From Job Search tab, click 'Open Reach out' on a job card to bring it here.")
    else:
        st.subheader("Selected job")
        st.json(selected["job"])
        st.markdown("**Placeholder for reach-out logic** — implement in services.reachout")

# ---------------------------
# Rank action available from Job Search sidebar area (download / view)
# ---------------------------
if st.session_state["active_tab"] == "Job Search":
    st.markdown("---")
    if st.button("Collect & Deduplicate all jobs"):
        if collect_and_dedupe_jobs is None:
            st.error("Ranking utilities not found. Implement services.ranking.collect_and_dedupe_jobs")
        else:
            collected = collect_and_dedupe_jobs(st.session_state.get("job_results", {}))
            st.session_state["collected_jobs"] = collected
            st.success(f"Collected {len(collected)} unique jobs.")

    if st.button("Rank all jobs"):
        if rank_jobs is None:
            st.error("Ranking module not found. Implement services.ranking.rank_jobs")
        else:
            ranked = rank_jobs(st.session_state.get("collected_jobs", []), st.session_state.get("candidate_json", {}))
            st.session_state["ranked_jobs"] = ranked
            st.success(f"Ranking finished: {len(ranked)} jobs.")

    # show ranked if present
    if st.session_state.get("ranked_jobs"):
        st.markdown("### Ranked Jobs")
        ranked = st.session_state["ranked_jobs"]
        # downloads
        st.download_button("Download ranked JSON", data=json.dumps(ranked, ensure_ascii=False, indent=2), file_name="ranked_jobs.json")
        df_ranked = pd.DataFrame(ranked)
        tmpf = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        df_ranked.to_csv(tmpf.name, index=False)
        with open(tmpf.name, "rb") as f:
            st.download_button(label="Download ranked CSV", data=f, file_name=os.path.basename(tmpf.name))

        for r in ranked:
            if render_job_card_with_score is None:
                st.write(r)
            else:
                st.markdown(render_job_card_with_score(r, float(r.get("relevance_score", 0.0))), unsafe_allow_html=True)

st.markdown("---")
st.caption("This app.py contains only UI and file reading logic. Implement business logic in services/ and UI helpers in ui_helpers.py")