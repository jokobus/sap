#!/usr/bin/env python3
"""GitHub Portfolio Analyzer

Pulls public GitHub repos, analyzes them, and creates detailed project summaries
to enhance cover letter, job matcher, project feedback, and resume tailor agents.

Usage:
  export GOOGLE_API_KEY="your-key"
  export GITHUB_USERNAME="your-github-username"  # optional, will try to find from resume
  python3 github_analyzer.py
"""

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any
from google import genai
import urllib.request
import urllib.error


def get_github_username_from_resume(resume: dict) -> str:
    """Extract GitHub username from resume profiles or project URLs."""
    # Try profiles first
    profiles = resume.get('basics', {}).get('profiles', [])
    for profile in profiles:
        if 'github' in profile.get('url', '').lower():
            url = profile['url']
            match = re.search(r'github\.com/([^/]+)', url)
            if match:
                return match.group(1)
    
    # Try project URLs
    projects = resume.get('projects', [])
    for project in projects:
        url = project.get('url', '') or ''
        if 'github.com' in url.lower():
            match = re.search(r'github\.com/([^/]+)', url)
            if match:
                return match.group(1)
    
    return None


def fetch_github_repos(username: str, max_repos: int = 10) -> List[Dict]:
    """Fetch public repos from GitHub API (no auth needed for public repos)."""
    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page={max_repos}"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/vnd.github.v3+json')
        req.add_header('User-Agent', 'Python-GitHub-Analyzer')
        
        with urllib.request.urlopen(req) as response:
            repos = json.loads(response.read().decode())
            return repos
    except urllib.error.HTTPError as e:
        print(f"Error fetching repos: {e.code} {e.reason}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


def fetch_repo_readme(owner: str, repo: str) -> str:
    """Fetch README content from a repo."""
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/vnd.github.v3.raw')
        req.add_header('User-Agent', 'Python-GitHub-Analyzer')
        
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8', errors='ignore')[:3000]  # Limit size
    except:
        return ""


def analyze_repos_with_ai(repos: List[Dict], resume_projects: List[Dict], api_key: str) -> Dict:
    """Use AI to analyze repos and create detailed summaries."""
    client = genai.Client(api_key=api_key)
    
    # Build repo summaries
    repo_summaries = []
    for repo in repos[:10]:  # Top 10 repos
        readme = fetch_repo_readme(repo['owner']['login'], repo['name'])
        summary = {
            'name': repo['name'],
            'description': repo.get('description', 'No description'),
            'url': repo['html_url'],
            'language': repo.get('language', 'Unknown'),
            'stars': repo.get('stargazers_count', 0),
            'topics': repo.get('topics', []),
            'readme_snippet': readme[:500] if readme else 'No README'
        }
        repo_summaries.append(summary)
    
    # Build resume projects list
    project_names = [p.get('name', '') for p in resume_projects]
    
    prompt = f"""Analyze these GitHub repositories and create detailed project summaries.

RESUME PROJECTS:
{', '.join(project_names)}

GITHUB REPOSITORIES:
{json.dumps(repo_summaries, indent=2)}

Create a JSON object with:
1. "matched_projects": Array of repos that match resume projects (include name, technologies, key_features, impact)
2. "top_showcase_repos": Top 3 repos to showcase (not in resume) with detailed analysis
3. "technical_summary": Overall tech stack and expertise demonstrated
4. "application_tips": How to leverage these repos in job applications

Keep each repo analysis to 2-3 sentences. Return ONLY valid JSON."""

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    text = response.text.strip()
    # Extract JSON
    start = text.find('{')
    end = text.rfind('}') + 1
    if start >= 0 and end > start:
        json_text = text[start:end]
    else:
        json_text = text
    
    try:
        return json.loads(json_text)
    except:
        return {
            'error': 'Failed to parse AI response',
            'raw_response': text,
            'repos': repo_summaries
        }


def main() -> None:
    API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # Read resume
    with open('Shishir_Sunar.resume.json', 'r', encoding='utf-8') as f:
        resume = json.load(f)
    
    # Get GitHub username
    github_username = os.environ.get('GITHUB_USERNAME')
    if not github_username:
        github_username = get_github_username_from_resume(resume)
    
    if not github_username:
        print('GitHub username not found. Please set GITHUB_USERNAME environment variable.')
        print('export GITHUB_USERNAME="your-username"')
        return
    
    print(f'Fetching GitHub repos for: {github_username}')
    repos = fetch_github_repos(github_username)
    
    if not repos:
        print('No public repos found or error fetching repos.')
        return
    
    print(f'Found {len(repos)} public repositories')
    print('Analyzing with AI...\n')
    
    # Analyze repos
    resume_projects = resume.get('projects', [])
    analysis = analyze_repos_with_ai(repos, resume_projects, API_KEY)
    
    # Add metadata
    result = {
        'generated_at': datetime.now().isoformat(),
        'github_username': github_username,
        'total_repos_analyzed': len(repos),
        'analysis': analysis,
        'raw_repos': repos[:5]  # Store top 5 raw repo data
    }
    
    # Save detailed analysis
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'github_portfolio_analysis_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print('='*60)
    print('GITHUB PORTFOLIO ANALYSIS')
    print('='*60)
    print(json.dumps(analysis, indent=2))
    print('='*60)
    print(f'\nDetailed analysis saved to: {output_file}')
    print('\nThis analysis can now be used by:')
    print('  - cover_letter_agent.py')
    print('  - job_matcher.py')
    print('  - project_feedback.py')
    print('  - resume_tailor.py')


if __name__ == '__main__':
    main()
