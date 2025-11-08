#!/usr/bin/env python3
"""Job Matcher Agent

Reads multiple job descriptions and ranks top 3 jobs based on resume fit.

Usage:
  export GOOGLE_API_KEY="your-key"
  ./venv/bin/python job_matcher.py
"""

import json
import os
from datetime import datetime
from google import genai


def main() -> None:
    API_KEY = os.environ.get('GOOGLE_API_KEY', 'AIzaSyCdpcLoI53VCunQagRNfQoZjvIALFANHEY')
    if not API_KEY:
        print('Please set GOOGLE_API_KEY environment variable and retry.')
        return

    client = genai.Client(api_key=API_KEY)

    # Read job descriptions
    with open('job_descriptions.json', 'r', encoding='utf-8') as f:
        jobs = json.load(f)

    # Read resume
    with open('Shishir_Sunar.resume.json', 'r', encoding='utf-8') as f:
        resume = json.load(f)

    # Build concise resume summary
    basics = resume.get('basics', {})
    education = resume.get('education', [])
    work = resume.get('work', [])
    skills = [s.get('name') for s in resume.get('skills', [])[:20]]
    projects = resume.get('projects', [])

    current_role = f"{work[0].get('position')} at {work[0].get('name')}" if work else "Student"
    resume_summary = f"""Name: {basics.get('name')}
Education: {', '.join([f"{e.get('studyType')} in {e.get('area')}" for e in education[:2]])}
Current: {current_role}
Skills: {', '.join(skills)}
Key Projects: {', '.join([p.get('name') for p in projects[:5]])}"""

    # Format jobs for prompt
    jobs_text = '\n\n'.join([
        f"JOB {i+1} [{j['id']}]:\nTitle: {j['title']}\nCompany: {j['company']}\nLocation: {j['location']}\nDescription: {j['description'][:300]}..."
        for i, j in enumerate(jobs)
    ])

    prompt = f"""Rank these jobs by fit for this candidate. Return ONLY a JSON array with top 3 jobs.

CANDIDATE SUMMARY:
{resume_summary}

AVAILABLE JOBS:
{jobs_text}

Return JSON array with EXACTLY this format (no extra text):
[
  {{"rank": 1, "job_id": "jobX", "match_score": 95, "reason": "One sentence why this is the best fit"}},
  {{"rank": 2, "job_id": "jobY", "match_score": 85, "reason": "One sentence why this is second best"}},
  {{"rank": 3, "job_id": "jobZ", "match_score": 75, "reason": "One sentence why this is third best"}}
]"""

    print('Analyzing job matches...\n')
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )

    # Extract JSON from response
    text = response.text.strip()
    # Find JSON array
    start = text.find('[')
    end = text.rfind(']') + 1
    if start >= 0 and end > start:
        json_text = text[start:end]
    else:
        json_text = text

    try:
        rankings = json.loads(json_text)
    except:
        print('Failed to parse response. Raw output:')
        print(text)
        return

    # Display results
    print('='*60)
    print('TOP 3 JOB MATCHES')
    print('='*60)
    
    for rank_data in rankings:
        job_id = rank_data['job_id']
        job = next((j for j in jobs if j['id'] == job_id), None)
        if job:
            print(f"\n{rank_data['rank']}. {job['title']} at {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Match Score: {rank_data['match_score']}%")
            print(f"   Why: {rank_data['reason']}")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output = f'job_matches_{timestamp}.json'
    
    result = {
        'generated_at': datetime.now().isoformat(),
        'top_matches': rankings,
        'job_details': [next((j for j in jobs if j['id'] == r['job_id']), None) for r in rankings]
    }
    
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f'\n{"="*60}')
    print(f'Results saved to: {output}')


if __name__ == '__main__':
    main()
