"""
Job Search Tab - Core job search and scraping functionality
"""
import streamlit as st
import pandas as pd
import tempfile
import os
from typing import List, Dict

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
        return [{"keyword": k, "location": loc or "Munich", "experience": experience} for k in keywords[:5]]

try:
    from services.job_scraper.job_scraper import scrape_linkedin_jobs
except Exception:
    scrape_linkedin_jobs = None


def render_job_card(job: dict, query_idx: int, job_idx: int) -> str:
    """
    Render a job card with HTML formatting
    """
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

    skill_html = ''.join([
        f"<span style='display:inline-block;padding:3px 8px;margin:2px;border-radius:12px;"
        f"border:1px solid #ddd;font-size:12px'>{s}</span>" 
        for s in skills
    ])

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


def build_queries_and_run_scraper(pages: int, results_per_page: int, max_workers: int):
    """
    Build job queries and (optionally) run scraper per query. 
    Saves job_results in session_state.
    """
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


def render_job_search_tab():
    """
    Render the Job Search tab - core functionality (scraper + cards)
    """
    st.header("Job Search")
    
    if not st.session_state.get("candidate_json"):
        st.info("No saved profile. Go to the Profile tab and click Save Profile first.")
        return
    
    st.write("Profile found. You can generate queries & run the scraper for the saved profile.")
    
    # Get scraper settings from sidebar session state
    pages = st.session_state.get("sid_pages", 2)
    results_per_page = st.session_state.get("sid_results", 5)
    max_workers = st.session_state.get("sid_workers", 4)
    
    if st.button("Generate job queries & run scraper"):
        with st.spinner("Building queries and scraping..."):
            build_queries_and_run_scraper(pages, results_per_page, max_workers)
        st.success("Queries generated and scraper run (or demo placeholders created).")

    if not st.session_state.get("job_queries"):
        st.info("No job queries available. Click 'Generate job queries & run scraper' to produce queries.")
        return
    
    queries = st.session_state["job_queries"]
    for i, q in enumerate(queries, start=1):
        st.markdown(f"---\n### Query {i}: **{q['keyword']}** — {q['location']} — {q['experience']}")
        df = st.session_state["job_results"].get(
            i-1, 
            pd.DataFrame(columns=["title", "company", "location", "url", "description", "skills"])
        )
        
        if df is None or df.empty:
            st.info("No results found for this query.")
            continue

        # CSV download per query
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        df.to_csv(tmp.name, index=False)
        with open(tmp.name, "rb") as f:
            st.download_button(
                label=f"Download CSV for '{q['keyword']}'", 
                data=f, 
                file_name=os.path.basename(tmp.name)
            )

        # Show up to first 20 results as cards with a separate 'Open Reach out' button
        rows_to_show = min(20, len(df))
        for idx in range(rows_to_show):
            job = df.iloc[idx].to_dict()
            html = render_job_card(job, i-1, idx)
            st.markdown(html, unsafe_allow_html=True)
            if st.button("Open Reach out (placeholder)", key=f"open_reach_{i-1}_{idx}"):
                st.session_state["selected_job"] = {
                    "query_index": i-1, 
                    "job_index": idx, 
                    "job": job
                }
                st.session_state["active_tab"] = "Reach out"
                st.rerun()

        # Dataframe expander
        with st.expander(f"Show table for query '{q['keyword']}' ({len(df)} results)"):
            st.dataframe(df)
