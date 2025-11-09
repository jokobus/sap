#!/usr/bin/env python3
"""Test script for reach-out workflow"""

import json
import sys
from pathlib import Path

# Add services to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.keyword_extractor.keyword_extractor import extract_job_keywords
from services.reach_out_generator.reach_out_generator import generate_reach_out_message


def test_keyword_extraction():
    """Test keyword extraction"""
    print("=" * 60)
    print("Testing Keyword Extraction")
    print("=" * 60)
    
    sample_job = {
        "title": "Presales Consultant (all people)",
        "company": "Instaffo",
        "location": "Munich",
        "description": """Presales Consultant (all people) bei ExB Labs GmbH

Anforderungen

Wohnsitz: Nur für Bewerber aus Deutschland

Sprache: Deutsch - Fließend, Englisch - Fließend

- Du hast Erfahrungen im technischen Presales oder in der technischen Beratung gesammelt – idealerweise im SaaS- oder KI-Umfeld.
- Du bringst einen Master in Informatik, Wirtschaftsinformatik oder eine vergleichbare Qualifikation mit technischer Ausrichtung mit.
- Du hast praktische Erfahrung im Umgang mit KI-Technologien, insbesondere LLMs, und kannst Jupyter Notebooks einsetzen, um APIs zu testen und unsere Plattform zu integrieren.
"""
    }
    
    try:
        result = extract_job_keywords(sample_job)
        print("\n✅ Keyword Extraction Successful!")
        print(f"\nExtracted Keywords: {', '.join(result['keywords'])}")
        print(f"\nSearch Query: {result['search_query']}")
        print(f"\nReasoning: {result.get('reasoning', 'N/A')}")
        return result
    except Exception as e:
        print(f"\n❌ Keyword Extraction Failed: {e}")
        return None


def test_message_generation():
    """Test message generation"""
    print("\n" + "=" * 60)
    print("Testing Message Generation")
    print("=" * 60)
    
    sample_job = {
        "title": "Senior Python Developer",
        "company": "TechCorp",
        "location": "Berlin",
        "description": "We're looking for a Senior Python Developer with ML experience to join our data science team. You will work on cutting-edge AI projects using Python, TensorFlow, and cloud technologies."
    }
    
    sample_candidate = {
        "contact_info": {
            "name": "John Doe",
            "headline": "Python Developer & ML Engineer",
            "location": "Berlin"
        },
        "skills": [
            {"skills": ["Python", "Machine Learning", "TensorFlow", "Docker", "AWS"]}
        ],
        "experience": [
            {
                "title": "Senior Python Developer",
                "company": "StartupXYZ",
                "description": "Led ML projects"
            }
        ],
        "education": [
            {
                "degree": "MSc Computer Science",
                "institution": "Technical University"
            }
        ]
    }
    
    try:
        # Test LinkedIn connection request
        print("\n--- LinkedIn Connection Request ---")
        message = generate_reach_out_message(
            job_data=sample_job,
            candidate_json=sample_candidate,
            message_type="linkedin_connection",
            tone="professional",
            keywords=["Python", "Machine Learning"]
        )
        print(f"\nSubject: {message['subject']}")
        print(f"\nBody:\n{message['body']}")
        print(f"\nCharacter count: {len(message['body'])}")
        
        # Test LinkedIn message
        print("\n--- LinkedIn InMail ---")
        message = generate_reach_out_message(
            job_data=sample_job,
            candidate_json=sample_candidate,
            message_type="linkedin_message",
            tone="enthusiastic"
        )
        print(f"\nSubject: {message['subject']}")
        print(f"\nBody:\n{message['body']}")
        
        # Test email
        print("\n--- Email ---")
        message = generate_reach_out_message(
            job_data=sample_job,
            candidate_json=sample_candidate,
            message_type="email",
            tone="professional"
        )
        print(f"\nSubject: {message['subject']}")
        print(f"\nBody:\n{message['body']}")
        
        print("\n✅ Message Generation Successful!")
        return True
    except Exception as e:
        print(f"\n❌ Message Generation Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_workflow():
    """Test the complete workflow"""
    print("\n" + "=" * 60)
    print("Testing Complete Workflow")
    print("=" * 60)
    
    job_data = {
        "title": "Presales Consultant",
        "company": "ExB Labs GmbH",
        "location": "Munich",
        "description": """We're looking for a Presales Consultant with experience in SaaS and AI/ML.
        Requirements: Master's in Computer Science, experience with LLMs, Python, Jupyter Notebooks, API integration.
        You'll conduct technical workshops, create demos, and work with Product and Engineering teams."""
    }
    
    candidate = {
        "contact_info": {
            "name": "Jane Smith",
            "headline": "Technical Consultant | SaaS & AI Solutions",
            "location": "Munich"
        },
        "skills": [
            {"skills": ["Python", "LLMs", "SaaS", "Presales", "API Integration"]}
        ],
        "experience": [
            {
                "title": "Technical Consultant",
                "company": "CloudTech GmbH",
                "description": "Conducted technical workshops for SaaS clients"
            }
        ]
    }
    
    # Step 1: Extract keywords
    print("\n1️⃣ Extracting keywords...")
    keywords_result = extract_job_keywords(job_data)
    if not keywords_result:
        print("Failed to extract keywords")
        return False
    
    print(f"Keywords: {', '.join(keywords_result['keywords'])}")
    
    # Step 2: Simulate LinkedIn search (not actually calling API)
    print("\n2️⃣ Would search LinkedIn with query:")
    print(f"   {keywords_result['search_query']}")
    
    # Step 3: Generate message
    print("\n3️⃣ Generating outreach message...")
    message = generate_reach_out_message(
        job_data=job_data,
        candidate_json=candidate,
        message_type="linkedin_connection",
        tone="professional",
        keywords=keywords_result['keywords']
    )
    
    print("\n📨 Generated Message:")
    print(f"Subject: {message['subject']}")
    print(f"\n{message['body']}")
    print(f"\n💡 Tips:")
    for tip in message.get('tips', []):
        print(f"   • {tip}")
    
    print("\n✅ Complete Workflow Test Successful!")
    return True


def main():
    """Run all tests"""
    print("\n🧪 Starting Reach-Out Workflow Tests\n")
    
    results = []
    
    # Test 1: Keyword Extraction
    try:
        kw_result = test_keyword_extraction()
        results.append(("Keyword Extraction", kw_result is not None))
    except Exception as e:
        print(f"❌ Keyword Extraction Test Error: {e}")
        results.append(("Keyword Extraction", False))
    
    # Test 2: Message Generation
    try:
        msg_result = test_message_generation()
        results.append(("Message Generation", msg_result))
    except Exception as e:
        print(f"❌ Message Generation Test Error: {e}")
        results.append(("Message Generation", False))
    
    # Test 3: Full Workflow
    try:
        workflow_result = test_full_workflow()
        results.append(("Full Workflow", workflow_result))
    except Exception as e:
        print(f"❌ Full Workflow Test Error: {e}")
        results.append(("Full Workflow", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check errors above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
