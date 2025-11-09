#!/usr/bin/env python3
"""Cover Letter Generator using Google Gemini API"""

import json
import os
from datetime import datetime
from google import genai


def main():
    # Config
    API_KEY = os.environ.get('GOOGLE_API_KEY')
    JOB_FILE = "job_description.txt"
    RESUME_FILE = "Shishir_Sunar.resume.json"
    OUTPUT_FILE = f"cover_letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    # Initialize Gemini client
    client = genai.Client(api_key=API_KEY)
    
    # Read files
    with open(JOB_FILE, 'r') as f:
        job_desc = f.read()
    
    with open(RESUME_FILE, 'r') as f:
        resume = json.load(f)
    
    # Check for GitHub analysis
    github_context = ""
    try:
        github_files = sorted([f for f in os.listdir('.') if f.startswith('github_portfolio_analysis_')])
        if github_files:
            with open(github_files[-1], 'r') as f:
                github_data = json.load(f)
                analysis = github_data.get('analysis', {})
                if 'technical_summary' in analysis:
                    github_context = f"\n\nGITHUB PORTFOLIO INSIGHTS:\n{analysis.get('technical_summary', '')}"
    except:
        pass
    
    # Format resume summary
    basics = resume.get('basics', {})
    summary = f"""Name: {basics.get('name')}
Education: {', '.join([f"{e.get('studyType')} in {e.get('area')} from {e.get('institution')}" for e in resume.get('education', [])[:2]])}
Experience: {', '.join([f"{w.get('position')} at {w.get('name')}" for w in resume.get('work', [])[:3]])}
Skills: {', '.join([s.get('name') for s in resume.get('skills', [])[:15]])}""" + github_context
    
    # Generate cover letter
    prompt = f"""Write a professional cover letter (3-4 paragraphs) for this job posting.
    
JOB DESCRIPTION:
{job_desc}

CANDIDATE:
{summary}

Requirements:
- Address specific job requirements
- Highlight relevant experience
- Show enthusiasm
- Professional tone
- Include greeting and closing"""
    
    print("Generating cover letter...")
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    # Save and display
    with open(OUTPUT_FILE, 'w') as f:
        f.write(response.text)
    
    print("\n" + "="*60)
    print(response.text)
    print("="*60)
    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
