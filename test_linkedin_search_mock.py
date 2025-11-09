#!/usr/bin/env python3
"""
Simple test script with MOCK data to demonstrate the functionality
Run: python test_linkedin_search_mock.py
"""

import json


def test_with_mock_data():
    """Test with mock LinkedIn search results"""
    
    print("=" * 60)
    print("Testing LinkedIn Search with MOCK DATA")
    print("=" * 60)
    
    # Dummy job data
    dummy_job = {
        "title": "Senior Python Developer",
        "company": "Google",
        "location": "Munich, Germany",
        "description": "We're looking for a Senior Python Developer with experience in Django, AWS, and microservices..."
    }
    
    # Dummy candidate data
    dummy_candidate = {
        "name": "John Doe",
        "skills": ["Python", "Django", "AWS", "Docker", "Kubernetes"],
        "experience": [
            {"title": "Software Engineer", "company": "Tech Corp", "duration": "2020-2023"}
        ]
    }
    
    # Extract keywords
    job_title_words = dummy_job["title"].split()
    keywords = [w for w in job_title_words if len(w) > 3][:3]
    
    print(f"\n📋 Job Information:")
    print(f"   Title: {dummy_job['title']}")
    print(f"   Company: {dummy_job['company']}")
    print(f"   Location: {dummy_job['location']}")
    
    print(f"\n👤 Candidate Information:")
    print(f"   Name: {dummy_candidate['name']}")
    print(f"   Skills: {', '.join(dummy_candidate['skills'])}")
    
    print(f"\n🔑 Extracted Keywords: {', '.join(keywords)}")
    
    # Build search query (what would be sent to LinkedIn search)
    search_query = f'(site:linkedin.com/in OR site:linkedin.com/pub) "{dummy_job["company"]}" "{dummy_job["location"]}" {" ".join(keywords)}'
    print(f"\n🔍 LinkedIn Search Query:")
    print(f"   {search_query}")
    
    # Mock LinkedIn search results
    mock_results = [
        {
            "rank": 1,
            "name": "Sarah Schmidt - Senior Python Engineer at Google",
            "url": "https://linkedin.com/in/sarah-schmidt-google",
            "snippet": "Senior Python Developer at Google Munich. Passionate about Django, AWS, and building scalable microservices. 8+ years experience in backend development.",
            "engine": "serpapi"
        },
        {
            "rank": 2,
            "name": "Michael Weber - Python Tech Lead at Google",
            "url": "https://linkedin.com/in/michael-weber-google-munich",
            "snippet": "Tech Lead for Python development at Google Munich. Expertise in cloud infrastructure, AWS, Docker, Kubernetes. Leading a team of 12 engineers.",
            "engine": "serpapi"
        },
        {
            "rank": 3,
            "name": "Lisa Müller - Senior Software Engineer",
            "url": "https://linkedin.com/in/lisa-mueller-google",
            "snippet": "Senior Software Engineer at Google. Working with Python, Django, and cloud technologies. Based in Munich, Germany.",
            "engine": "duckduckgo"
        },
        {
            "rank": 4,
            "name": "Thomas Klein - Engineering Manager at Google",
            "url": "https://linkedin.com/in/thomas-klein-google-munich",
            "snippet": "Engineering Manager at Google Munich. Hiring for Python developers. Background in full-stack development and microservices architecture.",
            "engine": "serpapi"
        },
        {
            "rank": 5,
            "name": "Anna Becker - Senior Backend Developer",
            "url": "https://linkedin.com/in/anna-becker-google",
            "snippet": "Senior Backend Developer specializing in Python and AWS at Google. Munich-based. Love building distributed systems.",
            "engine": "duckduckgo"
        }
    ]
    
    print("\n" + "=" * 60)
    print(f"MOCK RESULTS: {len(mock_results)} LINKEDIN PROFILES")
    print("=" * 60)
    
    print("\n📊 List of Relevant People to Contact:\n")
    
    for result in mock_results:
        print(f"{result['rank']}. {result['name']}")
        print(f"   🔗 Profile: {result['url']}")
        print(f"   📝 {result['snippet']}")
        print(f"   🔍 Found via: {result['engine'].upper()}")
        print()
    
    # Create summary table
    print("=" * 60)
    print("SUMMARY TABLE")
    print("=" * 60)
    print(f"{'#':<3} {'Name':<45} {'Source':<12}")
    print("-" * 60)
    for result in mock_results:
        name = result['name'][:43] + ".." if len(result['name']) > 45 else result['name']
        print(f"{result['rank']:<3} {name:<45} {result['engine'].upper():<12}")
    
    # Generate sample message for first contact
    contact = mock_results[0]
    candidate_name = dummy_candidate['name']
    candidate_skills = ', '.join(dummy_candidate['skills'][:3])
    
    print("\n" + "=" * 60)
    print("SAMPLE OUTREACH MESSAGE")
    print("=" * 60)
    
    sample_message = f"""Hi {contact['name'].split(' - ')[0]},

I came across your profile while researching {dummy_job['company']} and noticed you're working on {dummy_job['title']} opportunities in {dummy_job['location']}.

I'm {candidate_name}, and I have experience in {candidate_skills}. I'm very interested in the {dummy_job['title']} role at {dummy_job['company']}.

Would you be open to a brief conversation about the position and the team?

Best regards,
{candidate_name}

Profile: {contact['url']}"""
    
    print(sample_message)
    
    # Save to file
    output_file = "mock_linkedin_search_results.json"
    output_data = {
        "job": dummy_job,
        "candidate": dummy_candidate,
        "keywords": keywords,
        "search_query": search_query,
        "results": mock_results,
        "total_found": len(mock_results),
        "note": "These are MOCK results for demonstration purposes"
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)
    print(f"\n💾 Mock results saved to: {output_file}")
    print("\n📌 This demonstrates how the LinkedIn search would work:")
    print("   1. Extract keywords from job description and candidate data")
    print("   2. Build optimized LinkedIn search query")
    print("   3. Search for relevant people at the company")
    print("   4. Display names and profile links")
    print("   5. Generate personalized outreach messages")
    print("\n💡 To use real LinkedIn search:")
    print("   - Add SERPAPI_API_KEY to .env (recommended)")
    print("   - Or use DuckDuckGo (free but may have rate limits)")
    
    return mock_results


if __name__ == "__main__":
    results = test_with_mock_data()
    print(f"\n✨ Found {len(results)} contacts to reach out to!")
