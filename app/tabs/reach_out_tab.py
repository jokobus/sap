"""
Reach Out Tab - SIMPLIFIED: LinkedIn Profile Search Only
"""
import streamlit as st
import pandas as pd
import json
import os
import sys
from pathlib import Path

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

try:
    from linkedinsearch.search_linkedin import build_query, serpapi_search, ddg_html_search
except ImportError as e:
    st.error(f"Import error: {e}")
    build_query = None


def search_linkedin_profiles(keywords, company, location="", num_results=10):
    """Simple LinkedIn profile search"""
    try:
        # Force fresh import to get latest build_query function
        import importlib
        import sys
        if 'linkedinsearch.search_linkedin' in sys.modules:
            importlib.reload(sys.modules['linkedinsearch.search_linkedin'])
        from linkedinsearch.search_linkedin import build_query as bq
        
        # Clean company name for better search
        clean_company = company.replace(" & ", " ").replace("&", "") if company else company
        
        # Build simple query
        query = bq(keywords=keywords, company=clean_company, location=location)
        st.info(f"🔍 Search: `{query}`")
        
        # Show fallback strategies
        if company != clean_company:
            st.caption(f"📝 Using '{clean_company}' instead of '{company}' for better results")
        
        simple_query = bq(keywords=keywords[:2], company=clean_company, location="")
        st.caption(f"💡 Fallback: `{simple_query}`")
        
        # Try SerpAPI first
        serp_key = os.environ.get("SERPAPI_API_KEY")
        results = []
        
        if serp_key:
            try:
                results = serpapi_search(query, num=num_results, api_key=serp_key)
                st.success(f"✅ Found {len(results)} via SerpAPI")
            except Exception as e:
                st.warning(f"SerpAPI failed: {e}")
        
        # Fallback to DuckDuckGo
        if not results:
            results = ddg_html_search(query, num=num_results, debug=False)
        
        # If still no results, try simpler queries
        if not results and len(keywords) > 2:
            st.warning("🔄 No results with full query. Trying simpler search...")
            
            # Try with just company + top 2 keywords
            simple_query = bq(keywords=keywords[:2], company=company, location="")
            st.caption(f"Trying: {simple_query}")
            results = ddg_html_search(simple_query, num=num_results, debug=False)
            
            # Try with just company + 1 keyword
            if not results and keywords:
                minimal_query = bq(keywords=[keywords[0]], company=company, location="")
                st.caption(f"Trying: {minimal_query}")
                results = ddg_html_search(minimal_query, num=num_results, debug=False)
        
        return results if results else []
    except Exception as e:
        st.error(f"Search failed: {e}")
        return []


def render_reach_out_tab():
    """Simplified reach out tab - LinkedIn search only"""
    st.header("Find LinkedIn Contacts")
    
    # Check for selected job
    selected = st.session_state.get("selected_job")
    if not selected:
        st.info("No job selected. Go to Job Search tab and select a job first.")
        return
    
    job = selected["job"]
    
    # Display job info
    st.subheader(f"📋 {job.get('title', 'N/A')}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Company", job.get("company", "N/A"))
    with col2:
        st.metric("Location", job.get("location", "N/A"))
    with col3:
        num_profiles = st.number_input("Profiles", 5, 20, 10)
    
    st.markdown("---")
    
    # Smart keyword input
    st.markdown("### Keywords")
    st.caption("💡 **Tip:** Use 3-5 specific keywords like job level (Senior), skills (Python), or role (Developer) for best results")
    
    # Smart keyword extraction (3-5 words max)
    job_title = job.get('title', '')
    job_desc = job.get('description', '')
    
    # Extract better keywords from title and description
    def extract_keywords(text, max_words=5):
        # Common job keywords to prioritize
        important_words = [
            'Senior', 'Lead', 'Manager', 'Director', 'Principal', 'Architect', 'Junior',
            'Python', 'Java', 'JavaScript', 'React', 'Angular', 'Node', 'C++', 'Scala',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Cloud',
            'AI', 'ML', 'Data', 'Analytics', 'DevOps', 'Backend', 'Frontend',
            'Developer', 'Engineer', 'Consultant', 'Analyst', 'Scientist',
            'Machine', 'Learning', 'Deep', 'Neural', 'TensorFlow', 'PyTorch',
            'Research', 'Science', 'Intelligence', 'Algorithm', 'Model'
        ]
        
        words = []
        text_words = text.split()
        
        # Check for multi-word terms first
        multi_word_terms = ['Machine Learning', 'Data Science', 'Deep Learning', 'Software Engineer']
        for term in multi_word_terms:
            if term.lower() in text.lower() and term not in words:
                words.append(term)
                if len(words) >= max_words:
                    break
        
        # Then add individual important words (but skip words already in multi-word terms)
        used_words = set()
        for term in words:
            if ' ' in term:  # Multi-word term
                used_words.update(term.lower().split())
        
        # Skip common non-useful words
        skip_words = {'with', 'and', 'the', 'for', 'in', 'on', 'at', 'to', 'from', 'by', 'of', 'or', 'as', 'an', 'a'}
        
        for word in text_words:
            clean_word = word.strip('.,()[]{}":;!?').title()
            if (len(clean_word) > 2 and 
                clean_word.lower() not in used_words and  # Skip if part of multi-word term
                clean_word.lower() not in skip_words and  # Skip common words
                (clean_word in important_words or len(clean_word) > 3) and
                clean_word not in words):  # Avoid duplicates
                words.append(clean_word)
                if len(words) >= max_words:
                    break
        return words
    
    # Get suggested keywords
    title_keywords = extract_keywords(job_title, 3)
    desc_keywords = extract_keywords(job_desc, 2) if job_desc else []
    suggested = title_keywords + [k for k in desc_keywords if k not in title_keywords]
    suggested = suggested[:5]  # Max 5 keywords
    
    # Show extracted keywords for debugging
    if suggested:
        st.info(f"📋 Auto-extracted: {', '.join(suggested)}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        default_keywords = ", ".join(suggested[:4]) if suggested else "Senior, Engineer, Python, AWS"
        keywords_input = st.text_input(
            "Keywords (3-5 words max)",
            value=default_keywords,
            placeholder="e.g., Machine Learning, Senior, Engineer, Python",
            help="Enter 3-5 relevant keywords. Multi-word terms like 'Machine Learning' work best in quotes."
        )
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Parse and limit keywords - preserve multi-word terms
    keywords = []
    if keywords_input:
        for k in keywords_input.split(","):
            clean_k = k.strip()
            if clean_k:
                # Preserve case for multi-word terms, title case for single words
                if ' ' in clean_k:
                    keywords.append(clean_k)  # Keep "Machine Learning" as is
                else:
                    keywords.append(clean_k.title())  # "python" -> "Python"
    keywords = keywords[:5]  # Max 5
    
    if keywords:
        st.success(f"✅ Using {len(keywords)} keywords: {', '.join(keywords)}")
        
        # Debug: Show individual keywords
        st.caption(f"🔍 Individual keywords: {keywords}")
        
        # Show preview of search query
        from linkedinsearch.search_linkedin import build_query
        preview_query = build_query(keywords[:5], job.get("company", ""), job.get("location", ""))
        st.code(f"Query: {preview_query}", language="text")
        
        if len(keywords) > 3:
            st.info("💡 Using more keywords makes search more specific")
    else:
        st.warning("⚠️ Add some keywords for better results")
    
    # Search button
    st.markdown("---")
    if st.button("🔍 Search LinkedIn", use_container_width=True, type="primary"):
        if not keywords:
            st.error("⚠️ Enter at least one keyword!")
        else:
            with st.spinner("Searching..."):
                results = search_linkedin_profiles(
                    keywords=keywords[:5],  # Use up to 5 keywords
                    company=job.get("company", ""),
                    location=job.get("location", ""),
                    num_results=num_profiles
                )
                st.session_state["linkedin_search_results"] = results
                if results:
                    st.success(f"✅ Found {len(results)} profiles!")
                else:
                    st.warning("No results. Try different keywords.")
    
    # Display results
    if st.session_state.get("linkedin_search_results"):
        results = st.session_state["linkedin_search_results"]
        
        st.markdown("---")
        st.markdown(f"### 👥 {len(results)} LinkedIn Profiles")
        
        for i, result in enumerate(results, 1):
            name = result.get('name', 'Unknown')
            url = result.get('url', '#')
            snippet = result.get('snippet', '')
            
            with st.expander(f"{i}. {name}", expanded=(i <= 3)):
                st.markdown(f"🔗 **[Open Profile]({url})**")
                if snippet:
                    st.caption(snippet[:200])
                st.code(url, language="text")
        
        # Summary table
        st.markdown("---")
        st.markdown("### 📊 Summary")
        df = pd.DataFrame([
            {"#": i, "Name": r.get("name", "Unknown"), "URL": r.get("url", "")}
            for i, r in enumerate(results, 1)
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            "linkedin_contacts.csv",
            "text/csv",
            use_container_width=True
        )
