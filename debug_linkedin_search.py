#!/usr/bin/env python3
"""
Debug LinkedIn Search - Find out why no results are returned
"""

import os
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Add services to path
sys.path.insert(0, str(Path(__file__).parent / "services"))

def debug_linkedin_search():
    """Debug LinkedIn search to understand why no results"""
    
    print("=" * 60)
    print("DEBUGGING LINKEDIN SEARCH")
    print("=" * 60)
    
    # Test different query variations
    test_queries = [
        'site:linkedin.com/in "Rohde & Schwarz"',
        'site:linkedin.com/in "Machine Learning"',  
        'site:linkedin.com/in Munich',
        'site:linkedin.com/in Engineer',
        'linkedin.com/in "Rohde & Schwarz"',  # Without site: prefix
        '"Rohde & Schwarz" site:linkedin.com',  # Different order
        'site:linkedin.com "Rohde & Schwarz" Munich',  # Without /in
    ]
    
    # Test with DuckDuckGo manually
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing query: {query}")
        
        try:
            url = "https://html.duckduckgo.com/html/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.post(url, data={"q": query}, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Check if we got results
                if "linkedin.com/in" in response.text.lower():
                    print("   ✅ Found LinkedIn profiles!")
                    
                    # Count approximate results
                    linkedin_count = response.text.lower().count("linkedin.com/in")
                    print(f"   📊 Approximate {linkedin_count} LinkedIn links found")
                    
                elif "no results" in response.text.lower() or "didn't find" in response.text.lower():
                    print("   ❌ DuckDuckGo says no results")
                elif "captcha" in response.text.lower() or "verify" in response.text.lower():
                    print("   🚫 CAPTCHA/verification required")
                elif len(response.text) < 1000:
                    print("   ⚠️  Response too short - possible blocking")
                else:
                    print("   ❓ Unclear - response received but no clear LinkedIn links")
                    print(f"   📏 Response length: {len(response.text)} chars")
                    
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS & RECOMMENDATIONS")
    print("=" * 60)
    
    print("\n🔍 Possible Issues:")
    print("1. DuckDuckGo rate limiting/CAPTCHA")
    print("2. Company name 'Rohde & Schwarz' too specific")
    print("3. Location 'Munich, Bavaria, Germany' too detailed") 
    print("4. Search terms too restrictive")
    print("5. LinkedIn blocking automated searches")
    
    print("\n💡 Recommended Solutions:")
    print("1. Get SERPAPI_API_KEY (more reliable than DuckDuckGo)")
    print("2. Try broader searches:")
    print("   - Just company: 'Rohde Schwarz' (without &)")
    print("   - Just location: 'Munich'")
    print("   - Just role: 'Engineer'")
    print("3. Use alternative search engines")
    print("4. Wait and retry (rate limit may reset)")
    
    # Test the actual functions
    print("\n" + "=" * 60)
    print("TESTING ACTUAL SEARCH FUNCTIONS")
    print("=" * 60)
    
    try:
        from linkedinsearch.search_linkedin import build_query, ddg_html_search
        
        # Test query building
        keywords = ['Machine Learning', 'Engineer']
        company = 'Rohde & Schwarz'
        location = 'Munich'
        
        query = build_query(keywords, company, location)
        print(f"\n🔧 Built query: {query}")
        
        # Test simpler variations
        simple_queries = [
            build_query(['Engineer'], 'Rohde Schwarz', ''),  # No &, no location
            build_query(['Machine Learning'], '', 'Munich'),   # No company
            build_query(['Engineer'], '', ''),                 # Just keyword
        ]
        
        print(f"\n🔧 Simpler alternatives:")
        for sq in simple_queries:
            print(f"   {sq}")
        
        # Try actual search with simple query
        print(f"\n🔍 Testing actual search function...")
        results = ddg_html_search(simple_queries[0], num=3, debug=True)
        print(f"   Results: {len(results)} found")
        
        if results:
            print("   ✅ Search function works! Issue might be query specificity")
            for i, r in enumerate(results[:2], 1):
                print(f"   {i}. {r.get('name', 'Unknown')[:50]}...")
        else:
            print("   ❌ Even simple query returns no results - likely rate limited")
            
    except Exception as e:
        print(f"   💥 Error testing search functions: {e}")
    
    print("\n" + "=" * 60)
    print("FINAL DIAGNOSIS")
    print("=" * 60)
    print("Most likely cause: DuckDuckGo rate limiting or CAPTCHA")
    print("Best solution: Get SERPAPI_API_KEY for reliable results")
    print("Quick fix: Try simpler search terms and wait before retrying")


if __name__ == "__main__":
    debug_linkedin_search()