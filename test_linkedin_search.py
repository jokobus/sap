#!/usr/bin/env python3
"""
Standalone test script for LinkedIn search functionality
Run: python test_linkedin_search.py
"""

import os
import sys
import json
from pathlib import Path

# Add services to path
sys.path.insert(0, str(Path(__file__).parent / "services"))

from linkedinsearch.search_linkedin import build_query, serpapi_search, ddg_html_search


def test_linkedin_search():
    """Test the LinkedIn search with dummy data"""
    
    print("=" * 60)
    print("Testing LinkedIn Search Functionality")
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
    
    # Extract simple keywords from job title
    job_title_words = dummy_job["title"].split()
    keywords = [w for w in job_title_words if len(w) > 3][:3]
    
    print(f"\n📋 Job: {dummy_job['title']}")
    print(f"🏢 Company: {dummy_job['company']}")
    print(f"📍 Location: {dummy_job['location']}")
    print(f"\n👤 Candidate: {dummy_candidate['name']}")
    print(f"💼 Skills: {', '.join(dummy_candidate['skills'][:3])}")
    print(f"\n🔑 Extracted Keywords: {', '.join(keywords)}")
    
    # Build search query
    query = build_query(
        keywords=keywords,
        company=dummy_job["company"],
        location=dummy_job["location"]
    )
    
    print(f"\n🔍 LinkedIn Search Query:")
    print(f"   {query}")
    
    # Try to search
    serp_key = os.environ.get("SERPAPI_API_KEY")
    
    results = []
    print("\n" + "=" * 60)
    print("Starting LinkedIn Profile Search...")
    print("=" * 60)
    
    if serp_key:
        print("\n✅ SERPAPI_API_KEY found - using SerpAPI for best results...")
        try:
            results = serpapi_search(query, num=5, api_key=serp_key)
            print(f"✅ SerpAPI returned {len(results)} results")
        except Exception as e:
            print(f"❌ SerpAPI failed: {e}")
            print("⚠️  Falling back to DuckDuckGo...")
            results = []
    else:
        print("\n⚠️  SERPAPI_API_KEY not found in environment")
        print("💡 Get free API key at: https://serpapi.com/")
        print("💡 Add to .env file: SERPAPI_API_KEY=your_key_here")
    
    # Fallback to DuckDuckGo
    if not results:
        print("\n🔍 Using DuckDuckGo (free, but less reliable)...")
        try:
            results = ddg_html_search(query, num=5, debug=False)
            print(f"✅ DuckDuckGo returned {len(results)} results")
        except Exception as e:
            print(f"❌ DuckDuckGo failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Display results
    print("\n" + "=" * 60)
    print(f"FOUND {len(results)} LINKEDIN PROFILES")
    print("=" * 60)
    
    if results:
        for i, result in enumerate(results, 1):
            name = result.get('name', 'Unknown Profile')
            url = result.get('url', 'N/A')
            snippet = result.get('snippet', 'No description')
            engine = result.get('engine', 'N/A')
            
            print(f"\n{i}. {name}")
            print(f"   🔗 Profile URL: {url}")
            if snippet:
                snippet_preview = snippet[:150] + "..." if len(snippet) > 150 else snippet
                print(f"   📝 Snippet: {snippet_preview}")
            print(f"   🔍 Found via: {engine.upper()}")
    else:
        print("\n❌ No profiles found!")
        print("\nPossible reasons:")
        print("  • DuckDuckGo rate limiting or CAPTCHA detection")
        print("  • Network connectivity issues")
        print("  • Keywords too restrictive")
        print("\nSuggestions:")
        print("  1. Add SERPAPI_API_KEY to your .env file (recommended)")
        print("  2. Try with different/fewer keywords")
        print("  3. Wait a few minutes before retrying")
        print("  4. Check your internet connection")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    
    # Save results to file for inspection
    if results:
        output_file = "test_linkedin_search_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "job": dummy_job,
                "candidate": dummy_candidate,
                "keywords": keywords,
                "search_query": query,
                "results": results,
                "total_found": len(results)
            }, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Full results saved to: {output_file}")
        print(f"   You can open this file to see all profile details")
    
    return results


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the test
    results = test_linkedin_search()
    
    # Exit with appropriate code
    sys.exit(0 if results else 1)
