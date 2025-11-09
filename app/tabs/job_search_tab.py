"""
Job Search Tab - Core job search and scraping functionality
"""
import streamlit as st
import pandas as pd
import tempfile
import os
from typing import List, Dict
from pydantic import BaseModel, RootModel
import google.generativeai as genai

class RankedJobParams(BaseModel):
    title: str
    company: str
    location: str
    url: str
    description: str
    skills: List[str]
    relevance_score: float

class RankedJobsList(RootModel[List[RankedJobParams]]):
    pass


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


def gemini_call_for_ranking(jobs: List[Dict], candidate_json: Dict) -> List[Dict]:
    """Rank jobs using Gemini. Falls back to original order if API/key unavailable.

    Expects `jobs` with keys: title, company, location, url, description, skills.
    Returns list of same items plus `relevance_score` (0..1), sorted desc.
    """
    import os, json as _json

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # No key — return baseline scores (0.5) preserving order
        out = []
        for j in jobs:
            jj = dict(j)
            jj.setdefault("relevance_score", 0.5)
            out.append(jj)
        return out

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = (
            "You are an expert job ranking assistant. Given the candidate profile and a list of job postings,\n"
            "Rank the jobs based on relevance to the candidate's skills and experience.\n"
            "Return ONLY a JSON array of objects sorted by descending relevance with keys: \n"
            "['title','company','location','url','description','skills','relevance_score'] where relevance_score is a float between 0 and 1.\n\n"
            f"Candidate Profile JSON:\n{_json.dumps(candidate_json)[:5000]}\n\n"
            f"Job Postings JSON (array):\n{_json.dumps(jobs)[:8000]}\n\n"
        )
        resp = model.generate_content(prompt)
        # Parse JSON
        try:
            data = _json.loads(resp.text)
        except Exception:
            # Try to extract first JSON array
            import re
            m = re.search(r"\[.*\]", resp.text, re.S)
            data = _json.loads(m.group(0)) if m else []

        # Validate minimally and fill defaults
        out = []
        for j in data:
            jj = {
                "title": j.get("title", ""),
                "company": j.get("company", ""),
                "location": j.get("location", ""),
                "url": j.get("url", ""),
                "description": j.get("description", ""),
                "skills": j.get("skills", []) or [],
                "relevance_score": float(j.get("relevance_score", 0.5)),
            }
            out.append(jj)
        # If empty, fallback to baseline
        if not out:
            for j in jobs:
                jj = dict(j)
                jj.setdefault("relevance_score", 0.5)
                out.append(jj)
        # Sort by relevance desc
        out.sort(key=lambda x: x.get("relevance_score", 0.0), reverse=True)
        return out
    except Exception:
        # On any error, fallback
        out = []
        for j in jobs:
            jj = dict(j)
            jj.setdefault("relevance_score", 0.5)
            out.append(jj)
        return out

def render_job_card1(job: dict, query_idx: int, job_idx: int) -> str:
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

    #TODO: Mofifying html card to show confidence percentage with nice modern UI
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


def render_job_card(job: dict, query_idx: int, job_idx: int) -> str:
    """
    Render a job card with HTML formatting and confidence percentage.
    """
    title = job.get('title', 'Unknown Title')
    company = job.get('company', 'Unknown Company')
    location = job.get('location', 'Unknown Location')
    url = job.get('url', '#')
    desc = job.get('description', '') or ''
    skills = job.get('skills', []) or []
    relevance = job.get('relevance_score', 0.0)  # confidence score 0-1

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

    # confidence bar HTML
    conf_percent = int(relevance * 100)
    conf_html = f"""
    <div style='margin-top:8px'>
        <div style='font-size:12px;color:#555;margin-bottom:2px'>Relevance: {conf_percent}%</div>
        <div style='background:#eee;border-radius:8px;height:10px;width:100%'>
            <div style='background:#0f62fe;height:100%;border-radius:8px;width:{conf_percent}%;'></div>
        </div>
    </div>
    """

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
      {conf_html}
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
    for i, q in enumerate(queries[:1]):
        if scrape_linkedin_jobs is None:
            df = pd.DataFrame(columns=["title", "company", "location", "url", "description", "skills"])
        else:
            try:
                df = scrape_linkedin_jobs(
                    keywords=q["keyword"],
                    location=q.get("location", ""),
                    experience=q.get("experience", ""),
                    pages=1,
                    results_per_page=2,
                    max_workers=1,
                    out_csv=None,
                )
            except Exception as e:
                st.error(f"Scraper error for query {q}: {e}")
                df = pd.DataFrame(columns=["title", "company", "location", "url", "description", "skills"])
        # normalize: ensure DataFrame
        if df is None:
            df = pd.DataFrame(columns=["title", "company", "location", "url", "description", "skills"])

        ranked_jobs = gemini_call_for_ranking(df.to_dict(orient="records"), candidate_json)
        #convert it back to DataFrame with all keys that JSON has
        df = pd.DataFrame(ranked_jobs)
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
            if st.button("Open Reach out", key=f"open_reach_{i-1}_{idx}"):
                st.session_state["selected_job"] = {
                    "query_index": i-1, 
                    "job_index": idx, 
                    "job": job
                }
                st.session_state["nav_to_tab"] = "Reach out"
                st.rerun()

        # Dataframe expander
        with st.expander(f"Show table for query '{q['keyword']}' ({len(df)} results)"):
            st.dataframe(df)
