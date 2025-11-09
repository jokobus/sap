# Reach Out Integration Guide

## Overview
This document explains the complete reach-out workflow integration, including keyword extraction, LinkedIn search, and message generation.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Reach Out Tab                           │
│  (app/tabs/reach_out_tab.py)                               │
└────────┬────────────────────────────────────────────┬──────┘
         │                                            │
         ▼                                            ▼
┌─────────────────────┐                    ┌──────────────────────┐
│ Keyword Extractor   │                    │  Message Generator   │
│ (services/keyword_  │                    │  (services/reach_    │
│  extractor/)        │                    │   out_generator/)    │
└────────┬────────────┘                    └──────────────────────┘
         │                                            │
         ▼                                            ▼
┌─────────────────────┐                    ┌──────────────────────┐
│ LinkedIn Search     │                    │  Candidate JSON      │
│ (services/linked    │                    │  (session_state)     │
│  insearch/)         │                    └──────────────────────┘
└─────────────────────┘
```

## Components

### 1. Keyword Extractor Service
**Location**: `services/keyword_extractor/keyword_extractor.py`

**Purpose**: Extract relevant keywords from job descriptions for LinkedIn search.

**Key Features**:
- AI-powered keyword extraction using Gemini
- HTML cleaning and text processing
- Intelligent keyword selection (skills, technologies, qualifications)
- Search query builder
- Fallback extraction for API failures

**Usage**:
```python
from services.keyword_extractor.keyword_extractor import extract_job_keywords

result = extract_job_keywords({
    "title": "Senior Python Developer",
    "company": "TechCorp",
    "location": "Berlin",
    "description": "Job description here..."
})

# Returns:
# {
#     "keywords": ["Python", "Machine Learning", "AWS", ...],
#     "job_title": "Senior Python Developer",
#     "company": "TechCorp",
#     "location": "Berlin",
#     "search_query": 'Python "Machine Learning" AWS "TechCorp"',
#     "reasoning": "Why these keywords were chosen..."
# }
```

### 2. Reach Out Message Generator
**Location**: `services/reach_out_generator/reach_out_generator.py`

**Purpose**: Generate personalized outreach messages based on job and candidate profile.

**Message Types**:
- `linkedin_connection`: Connection request (max 300 chars)
- `linkedin_message`: InMail or direct message (400-600 chars)
- `email`: Professional email (3-4 paragraphs)

**Tone Options**:
- `professional`: Formal business tone
- `friendly`: Warm but professional
- `enthusiastic`: Energetic and passionate

**Usage**:
```python
from services.reach_out_generator.reach_out_generator import generate_reach_out_message

message = generate_reach_out_message(
    job_data={
        "title": "Senior Python Developer",
        "company": "TechCorp",
        "description": "..."
    },
    candidate_json=candidate_profile,  # From aggregator
    message_type="linkedin_connection",
    tone="professional",
    keywords=["Python", "ML"]  # Optional
)

# Returns:
# {
#     "subject": "Connection request note",
#     "body": "The actual message",
#     "short_version": "Shorter version if needed",
#     "tips": ["tip1", "tip2"],
#     "message_type": "linkedin_connection",
#     "tone": "professional"
# }
```

### 3. LinkedIn Search Integration
**Location**: `services/linkedinsearch/search_linkedin.py`

**Purpose**: Search for LinkedIn profiles using keywords.

**Features**:
- Dual engine support (SerpAPI + DuckDuckGo)
- Profile-focused search (excludes company pages, job listings)
- Smart query building
- Result ranking and filtering

**Usage** (from reach_out_tab):
```python
from services.linkedinsearch.search_linkedin import build_query, serpapi_search, ddg_html_search

query = build_query(["Python", "ML"], "TechCorp")
results = serpapi_search(query, num=10, api_key=api_key)
# Or fallback:
results = ddg_html_search(query, num=10)
```

### 4. Reach Out Tab UI
**Location**: `app/tabs/reach_out_tab.py`

**Purpose**: Streamlit UI for the complete reach-out workflow.

**Features**:
- Three main tabs:
  1. **Find Contacts**: Extract keywords and search LinkedIn
  2. **Generate Message**: Create personalized outreach messages
  3. **Contact Manager**: Track outreach activities

**Session State Variables**:
```python
st.session_state["extracted_keywords"]      # Keyword extraction result
st.session_state["linkedin_search_results"] # LinkedIn profile search results
st.session_state["selected_contact"]        # Currently selected contact
st.session_state["generated_message"]       # Generated outreach message
st.session_state["outreach_log"]            # List of logged outreach activities
```

## Installation

### 1. Install Dependencies
```bash
# Install for keyword extractor
pip install google-genai python-dotenv

# Install for LinkedIn search
pip install requests beautifulsoup4 serpapi
```

### 2. Set Environment Variables
```bash
# Required
export GOOGLE_API_KEY="your_gemini_api_key"

# Optional (for better LinkedIn search)
export SERPAPI_API_KEY="your_serpapi_key"
```

### 3. Verify Installation
```bash
python tests/test_reach_out_workflow.py
```

## Workflow

### User Journey

1. **Upload Profile** (Profile Tab)
   - Upload resume and/or LinkedIn PDF
   - System generates `candidate_json` via aggregator

2. **Search Jobs** (Job Search Tab)
   - Search for relevant jobs
   - Select a job and click "Open Reach out"

3. **Extract Keywords** (Reach Out Tab → Find Contacts)
   - Click "Extract Keywords from Job"
   - AI analyzes job description
   - Displays extracted keywords and reasoning

4. **Search LinkedIn** (Reach Out Tab → Find Contacts)
   - Adjust number of profiles to find
   - Click "Search LinkedIn Profiles"
   - Browse results and select a contact

5. **Generate Message** (Reach Out Tab → Generate Message)
   - Select message type and tone
   - Click "Generate Message"
   - AI creates personalized message using:
     - Job description
     - Candidate profile
     - Extracted keywords

6. **Track Outreach** (Reach Out Tab → Contact Manager)
   - Review generated message
   - Copy to clipboard
   - Log outreach activity
   - Export log as CSV

### Data Flow

```
Job Selection
    ↓
    st.session_state["selected_job"] = {
        "query_index": 0,
        "job_index": 0,
        "job": {
            "title": "...",
            "company": "...",
            "location": "...",
            "description": "...",
            "url": "..."
        }
    }
    ↓
Keyword Extraction (AI)
    ↓
    st.session_state["extracted_keywords"] = {
        "keywords": ["Python", "ML", ...],
        "search_query": "...",
        "reasoning": "..."
    }
    ↓
LinkedIn Search (API/DuckDuckGo)
    ↓
    st.session_state["linkedin_search_results"] = [
        {
            "rank": 1,
            "name": "John Doe",
            "url": "linkedin.com/in/johndoe",
            "snippet": "...",
            "engine": "serpapi"
        },
        ...
    ]
    ↓
Contact Selection
    ↓
    st.session_state["selected_contact"] = {...}
    ↓
Message Generation (AI + Candidate Profile)
    ↓
    st.session_state["generated_message"] = {
        "subject": "...",
        "body": "...",
        "short_version": "...",
        "tips": [...]
    }
    ↓
Outreach Logging
    ↓
    st.session_state["outreach_log"].append({
        "job_title": "...",
        "company": "...",
        "contact": {...},
        "message_type": "...",
        "timestamp": "..."
    })
```

## API Reference

### KeywordExtractor Class

```python
class KeywordExtractor:
    def __init__(self, api_key: Optional[str] = None)
    
    def extract_keywords(
        self,
        job_title: str,
        job_description: str,
        company: str = "",
        location: str = "",
        max_keywords: int = 8
    ) -> Dict[str, any]
```

### ReachOutGenerator Class

```python
class ReachOutGenerator:
    def __init__(self, api_key: Optional[str] = None)
    
    def generate_message(
        self,
        job_data: Dict,
        candidate_json: Dict,
        message_type: str = "linkedin_connection",
        tone: str = "professional",
        include_keywords: Optional[List[str]] = None
    ) -> Dict[str, str]
```

### LinkedIn Search Functions

```python
def build_query(
    keywords: List[str],
    company: Optional[str] = None
) -> str

def serpapi_search(
    query: str,
    num: int = 10,
    api_key: Optional[str] = None
) -> List[Dict]

def ddg_html_search(
    query: str,
    num: int = 10,
    dump_html: Optional[str] = None,
    debug: bool = False
) -> List[Dict]
```

## Error Handling

### Common Errors and Solutions

1. **"No candidate profile found"**
   - **Cause**: `st.session_state["candidate_json"]` is None
   - **Solution**: Go to Profile tab and upload resume/LinkedIn profile

2. **"Keyword extraction service not available"**
   - **Cause**: Import error or missing API key
   - **Solution**: Check `GOOGLE_API_KEY` environment variable

3. **"LinkedIn search returns no results"**
   - **Cause**: DuckDuckGo rate limiting or captcha
   - **Solution**: Use SerpAPI or try with fewer keywords

4. **"Import errors"**
   - **Cause**: Python path issues
   - **Solution**: Run from project root: `streamlit run app/app.py`

### Fallback Mechanisms

1. **Keyword Extraction**: Falls back to heuristic extraction if AI fails
2. **LinkedIn Search**: Falls back to DuckDuckGo if SerpAPI unavailable
3. **Message Generation**: Falls back to template-based messages if AI fails

## Testing

### Run All Tests
```bash
python tests/test_reach_out_workflow.py
```

### Test Individual Components
```bash
# Test keyword extraction
python services/keyword_extractor/keyword_extractor.py

# Test message generation
python services/reach_out_generator/reach_out_generator.py

# Test LinkedIn search
cd services/linkedinsearch
python search_linkedin.py --keywords "Python" "ML" --company "TechCorp"
```

## Performance Considerations

### AI API Calls
- **Keyword Extraction**: ~2-5 seconds per job
- **Message Generation**: ~3-7 seconds per message
- **Caching**: Results stored in session_state to avoid re-generation

### LinkedIn Search
- **SerpAPI**: ~1-3 seconds, requires API key
- **DuckDuckGo**: ~3-10 seconds, may hit rate limits
- **Recommendation**: Use SerpAPI for production

## Best Practices

1. **Always upload complete profile** before using reach-out features
2. **Review extracted keywords** and adjust search if needed
3. **Personalize generated messages** before sending
4. **Track all outreach** to avoid duplicate contacts
5. **Use professional tone** for initial contact
6. **Keep messages concise** especially for LinkedIn
7. **Export outreach log regularly** for record-keeping

## Future Enhancements

- [ ] Direct LinkedIn API integration
- [ ] Email sending functionality
- [ ] A/B testing for message variants
- [ ] Response tracking
- [ ] CRM integration
- [ ] Browser automation
- [ ] Contact deduplication
- [ ] Message template library
- [ ] Multi-language support
- [ ] Sentiment analysis for job descriptions

## Support

For issues or questions:
1. Check the troubleshooting section in `REACH_OUT_README.md`
2. Review test results from `test_reach_out_workflow.py`
3. Check service-specific README files
4. Review environment variable configuration
