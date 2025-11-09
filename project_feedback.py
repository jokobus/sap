#!/usr/bin/env python3
"""Project Relevance Feedback Agent

Analyzes resume projects against job description and provides customized feedback
on which projects are most relevant and why.

Usage:
  export GOOGLE_API_KEY="your-key"
  ./venv/bin/python project_feedback.py
"""

import json
import os
from datetime import datetime
from google import genai


def main() -> None:
    API_KEY = "AIzaSyCdpcLoI53VCunQagRNfQoZjvIALFANHEY"
    if not API_KEY:
        print('Please set GOOGLE_API_KEY environment variable and retry.')
        return

    client = genai.Client(api_key=API_KEY)

    with open('job_description.txt', 'r', encoding='utf-8') as f:
        job = f.read()

    with open('Shishir_Sunar.resume.json', 'r', encoding='utf-8') as f:
        resume = json.load(f)

    # Extract projects and work experience
    projects = resume.get('projects', [])
    work = resume.get('work', [])
    
    # Combine projects and work experience
    items = []
    for p in projects:
        items.append(f"PROJECT: {p.get('name', 'Unnamed')}: {p.get('summary', 'No summary')}")
    for w in work:
        items.append(f"WORK: {w.get('position', 'Position')} at {w.get('name', 'Company')}: {w.get('summary', 'No summary')}")
    
    if not items:
        print('No projects or work experience found.')
        return

    items_text = '\n'.join([f"{i+1}. {item}" for i, item in enumerate(items)])

    prompt = f"""Analyze which projects/experiences are most relevant for this job. Be CONCISE.

JOB:
{job}

CANDIDATE'S PROJECTS & EXPERIENCE:
{items_text}

Provide SHORT feedback:
1. Top 3 most relevant (1 sentence each why)
2. What to emphasize in application (2-3 bullet points max)

Keep response under 200 words total."""

    print('Analyzing project relevance...\n')
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )

    feedback = response.text
    
    # Save feedback
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output = f'project_feedback_{timestamp}.txt'
    
    with open(output, 'w', encoding='utf-8') as f:
        f.write(f"Project Relevance Feedback\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")
        f.write(feedback)
    
    print('='*60)
    print(feedback)
    print('='*60)
    print(f'\nFeedback saved to: {output}')


if __name__ == '__main__':
    main()
