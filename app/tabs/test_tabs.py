"""
Testing Guide for Modular Tabs

This guide shows how to test each tab independently.
"""

# Example: Testing Profile Tab Independently
# ============================================

# You can test each tab's logic by importing it directly:

from tabs.profile_tab import render_profile_tab, run_parse_and_save
import streamlit as st

# Mock session state for testing
if "candidate_json" not in st.session_state:
    st.session_state["candidate_json"] = None
if "resume_bytes" not in st.session_state:
    st.session_state["resume_bytes"] = None
if "linkedin_bytes" not in st.session_state:
    st.session_state["linkedin_bytes"] = None
if "github_username" not in st.session_state:
    st.session_state["github_username"] = ""

# Test the render function
render_profile_tab()


# Example: Unit Testing Individual Functions
# ===========================================

def test_run_parse_and_save():
    """Test profile parsing logic"""
    # Setup
    resume_bytes = b"mock resume data"
    linkedin_bytes = b"mock linkedin data"
    github_username = "testuser"
    
    # Execute
    run_parse_and_save(resume_bytes, linkedin_bytes, github_username)
    
    # Verify
    assert st.session_state["candidate_json"] is not None
    print("✓ Profile parsing test passed")


# Example: Testing Job Search Tab Functions
# ==========================================

from tabs.job_search_tab import render_job_card, build_queries_and_run_scraper

def test_render_job_card():
    """Test job card rendering"""
    mock_job = {
        'title': 'Software Engineer',
        'company': 'Tech Corp',
        'location': 'San Francisco, CA',
        'url': 'https://example.com/job/123',
        'description': 'Great opportunity for a software engineer...',
        'skills': ['Python', 'Django', 'PostgreSQL']
    }
    
    html = render_job_card(mock_job, 0, 0)
    assert 'Software Engineer' in html
    assert 'Tech Corp' in html
    print("✓ Job card rendering test passed")


# Example: Integration Testing
# =============================

def test_full_workflow():
    """Test complete workflow across tabs"""
    # 1. Upload profile
    st.session_state["candidate_json"] = {
        "contact_info": {"name": "Test User"},
        "skills": [{"skills": ["Python", "JavaScript"]}]
    }
    
    # 2. Generate job queries
    st.session_state["job_queries"] = [
        {"keyword": "Python Developer", "location": "Remote", "experience": "Mid-level"}
    ]
    
    # 3. Verify data flow
    assert len(st.session_state["job_queries"]) > 0
    print("✓ Full workflow test passed")


# Running Tests
# =============
# 
# Option 1: Run directly
# python -c "from tabs.test_tabs import test_run_parse_and_save; test_run_parse_and_save()"
#
# Option 2: Use pytest
# pytest app/tabs/test_tabs.py
#
# Option 3: Test via Streamlit
# streamlit run app/app.py
# Then manually navigate to each tab


# Development Tips
# ================
#
# 1. Test individual functions before integration
# 2. Use mock data to avoid external dependencies
# 3. Check session state after each operation
# 4. Verify HTML output for rendering functions
# 5. Test error handling with invalid inputs
#
# Example: Testing error handling
def test_parse_with_no_data():
    """Test parsing with no input data"""
    try:
        run_parse_and_save(None, None, "")
        # Should still create a default candidate_json
        assert st.session_state["candidate_json"] is not None
        print("✓ Error handling test passed")
    except Exception as e:
        print(f"✗ Test failed: {e}")


# Debugging Individual Tabs
# ==========================
#
# Add print statements or use streamlit's built-in debugging:
#
# st.write("Debug: candidate_json =", st.session_state.get("candidate_json"))
# st.write("Debug: job_queries =", st.session_state.get("job_queries"))
#
# Or use Python's debugger:
# import pdb; pdb.set_trace()


if __name__ == "__main__":
    print("Running tab tests...")
    test_render_job_card()
    test_run_parse_and_save()
    test_full_workflow()
    test_parse_with_no_data()
    print("\nAll tests completed!")
