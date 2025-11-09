# Reach Out Tab - Complete Workflow

## Overview
The Reach Out tab provides an end-to-end workflow for connecting with recruiters and hiring managers for job opportunities.

## Features

### 1. 🔍 Find Contacts
- **Keyword Extraction**: Automatically extracts the most relevant keywords from job descriptions using AI
- **LinkedIn Search**: Searches for relevant contacts on LinkedIn using extracted keywords
- **Smart Filtering**: Focuses on finding people profiles (not company pages or job listings)
- **Dual Search Engines**: Uses SerpAPI (if API key available) or DuckDuckGo as fallback

### 2. ✉️ Generate Message
- **Personalized Outreach**: Generates tailored messages based on:
  - Job description
  - Candidate profile (from aggregator)
  - Extracted keywords
  - Selected tone and message type
  
- **Multiple Message Types**:
  - LinkedIn Connection Request (under 300 chars)
  - LinkedIn InMail/Message (400-600 chars)
  - Professional Email (3-4 paragraphs)

- **Customizable Tone**:
  - Professional
  - Friendly
  - Enthusiastic

### 3. 📊 Contact Manager
- **Outreach Tracking**: Log your outreach activities
- **Export Functionality**: Download outreach log as CSV
- **Contact Management**: Keep track of selected contacts

## Workflow

1. **Select a Job** (from Job Search tab)
2. **Extract Keywords**: Click "Extract Keywords from Job" to analyze the job description
3. **Find Contacts**: Search LinkedIn for relevant people based on keywords
4. **Select Contact**: Choose a contact from search results
5. **Generate Message**: Create a personalized outreach message
6. **Log Outreach**: Track your outreach activity

## Requirements

### Environment Variables
```bash
GOOGLE_API_KEY=your_gemini_api_key
SERPAPI_API_KEY=your_serpapi_key  # Optional, uses DuckDuckGo if not set
```

### Python Dependencies
```bash
google-genai
python-dotenv
requests
beautifulsoup4
serpapi  # Optional
```

## Services Used

### 1. Keyword Extractor (`services/keyword_extractor/`)
- Extracts 5-8 most relevant keywords from job descriptions
- Uses Gemini AI for intelligent keyword selection
- Provides reasoning for keyword choices
- Builds optimized search queries

### 2. Reach Out Generator (`services/reach_out_generator/`)
- Generates personalized messages using Gemini AI
- Considers candidate profile, job description, and keywords
- Adapts tone and length based on message type
- Provides personalization tips

### 3. LinkedIn Search (`services/linkedinsearch/`)
- Searches for LinkedIn profiles using keywords
- Filters for people profiles only
- Supports multiple search engines (SerpAPI, DuckDuckGo)
- Returns ranked results with snippets

## Example Usage

### From Command Line

#### Extract Keywords
```python
from services.keyword_extractor.keyword_extractor import extract_job_keywords

job_data = {
    "title": "Senior Python Developer",
    "company": "TechCorp",
    "location": "Berlin",
    "description": "We're looking for..."
}

keywords = extract_job_keywords(job_data)
print(keywords)
```

#### Generate Message
```python
from services.reach_out_generator.reach_out_generator import generate_reach_out_message

message = generate_reach_out_message(
    job_data=job_data,
    candidate_json=candidate_profile,
    message_type="linkedin_connection",
    tone="professional",
    keywords=["Python", "Machine Learning"]
)

print(message["body"])
```

#### Search LinkedIn
```bash
cd services/linkedinsearch
python search_linkedin.py --keywords "Python" "Machine Learning" --company "TechCorp" --num 10
```

## Data Flow

```
Job Description
    ↓
[Keyword Extractor] → Keywords
    ↓
[LinkedIn Search] → Contact List
    ↓
[User Selection] → Selected Contact
    ↓
[Message Generator] → Personalized Message
    ↓
[Contact Manager] → Outreach Log
```

## Tips for Best Results

1. **Upload Complete Profile**: Ensure your resume and LinkedIn profile are uploaded in the Profile tab
2. **Review Keywords**: Check extracted keywords and adjust if needed
3. **Personalize Further**: Use the generated message as a template and add personal touches
4. **Track Outreach**: Log all activities to avoid duplicate contacts
5. **Use SerpAPI**: For best LinkedIn search results, set up SerpAPI (has free tier)

## Troubleshooting

### "No candidate profile found"
- Go to Profile tab and upload your resume/LinkedIn profile

### "Keyword extraction service not available"
- Check that `GOOGLE_API_KEY` is set in environment
- Ensure `google-genai` package is installed

### "LinkedIn search returns no results"
- Try with fewer, more specific keywords
- Check internet connection
- DuckDuckGo may require captcha solving in browser first

### "Import errors"
- Run from the correct directory: `streamlit run app/app.py`
- Ensure all dependencies are installed: `pip install -r requirements.txt`

## Future Enhancements

- [ ] Direct LinkedIn API integration (requires OAuth)
- [ ] Email sending functionality
- [ ] A/B testing for message variants
- [ ] Response tracking
- [ ] CRM integration
- [ ] Browser automation for LinkedIn
- [ ] Contact deduplication across jobs
- [ ] Message template library
