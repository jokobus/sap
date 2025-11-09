import streamlit as st
from dotenv import load_dotenv
import os
import asyncio
import tempfile
import pandas as pd
from typing import List, Dict

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


st.set_page_config(page_title="Resume → Job Matches", layout="wide")
load_dotenv()

st.title("Job Finder — Upload resume, LinkedIn and GitHub")
st.write("Upload your artifacts and get scraped job listings shown as cards.")

with st.sidebar:
    st.header("Inputs")
    resume_file = st.file_uploader("Upload resume PDF", type=["pdf"])
    linkedin_file = st.file_uploader("Upload LinkedIn profile PDF", type=["pdf"])
    github_username = st.text_input("GitHub username (optional)")
    pages = st.number_input("Pages per query (scraper)", value=2, min_value=1, max_value=10)
    results_per_page = st.number_input("Results per page (scraper)", value=5, min_value=1, max_value=25)
    max_workers = st.number_input("Scraper workers", value=4, min_value=1, max_value=16)
    submit = st.button("Generate job matches")

# Helper: render a single job as HTML card
def render_job_card(job: dict) -> str:
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
        <div>
          <div style='font-weight:700;font-size:16px'>{title}</div>
          <div style='color:#555;margin-top:4px'>{company} • {location}</div>
        </div>
        <div>
          <a href='{url}' target='_blank' style='background:#0f62fe;color:#fff;padding:8px 12px;border-radius:8px;text-decoration:none;font-weight:600'>Apply / Details</a>
        </div>
      </div>
      <div style='margin-top:12px;color:#333'>{desc_short}</div>
      <div style='margin-top:10px'>{skill_html}</div>
    </div>
    """
    return html


if submit:
    if not (resume_file or linkedin_file or github_username):
        st.error("Please upload at least a resume or LinkedIn PDF or provide a GitHub username.")
    else:
        with st.spinner("Parsing candidate profile and generating queries..."):
            try:
                resume_bytes = resume_file.read() if resume_file else None
                linkedin_bytes = linkedin_file.read() if linkedin_file else None

                if parse_all is not None:
                    # parse_all is expected to be async; run it synchronously here
                    candidate_json = asyncio.run(parse_all(resume_bytes, linkedin_bytes, github_username))
                else:
                    # Lightweight fallback candidate JSON
                    candidate_json = {
                        "contact_info": {"name": "Unknown", "location": "", "headline": ""},
                        "skills": [{"skills": ["Python", "Machine Learning", "Data Science"]}],
                        "data_sources": []
                    }
            except Exception as e:
                st.exception(e)
                candidate_json = None

        if candidate_json:
            st.success("Parsed candidate profile")
            # Show a compact preview
            with st.expander("Candidate preview (JSON)", expanded=False):
                st.json(candidate_json)

            # Build search queries
            try:
                job_queries = extract_job_search_queries(candidate_json)
            except Exception as e:
                st.warning("Failed to call your LLM-based extractor; falling back to heuristic queries.")
                job_queries = extract_job_search_queries(candidate_json)

            if not job_queries:
                st.info("No job queries produced. Try improving detected skills/headline in the uploaded files.")
            else:
                st.markdown(f"### Generated {len(job_queries)} search queries")
                # For each query, call scraper and show results
                for i, q in enumerate(job_queries, start=1):
                    st.markdown(f"---\n#### Query {i}: **{q['keyword']}** — {q['location']} — {q['experience']}")

                    if scrape_linkedin_jobs is None:
                        st.info("No scraper available in this environment. Showing demo empty result.")
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

                    if df is None or df.empty:
                        st.info("No results found for this query.")
                        continue

                    # allow user to download CSV for this query
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
                    df.to_csv(tmp.name, index=False)
                    with open(tmp.name, "rb") as f:
                        st.download_button(label=f"Download CSV for '{q['keyword']}'", data=f, file_name=os.path.basename(tmp.name))

                    # show first N results as cards
                    rows_to_show = min(20, len(df))
                    for idx in range(rows_to_show):
                        job = df.iloc[idx].to_dict()
                        st.markdown(render_job_card(job), unsafe_allow_html=True)

                    # also show the raw dataframe if user wants
                    with st.expander(f"Show table for query '{q['keyword']}' ({len(df)} results)"):
                        st.dataframe(df)

        else:
            st.error("Failed to parse candidate profile.")


# Footer
st.markdown("---")
st.caption("This app expects your existing pipeline functions: parse_all(candidate artifacts) and scrape_linkedin_jobs(...) to be importable. If they are not available the app will fall back to heuristics or show demo content. Update imports at the top to match your project structure.")
