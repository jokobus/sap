#!/usr/bin/env python3
"""Reach Out Message Generator - Create personalized outreach messages"""

import os
import json
from typing import Dict, List, Optional
from google import genai
from dotenv import load_dotenv

load_dotenv()


class ReachOutGenerator:
    """Generate personalized outreach messages for job opportunities"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the reach out generator with Gemini API"""
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.0-flash"
    
    def generate_message(
        self,
        job_data: Dict,
        candidate_json: Dict,
        message_type: str = "linkedin_connection",
        tone: str = "professional",
        keywords: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate a personalized outreach message.
        
        Args:
            job_data: Dictionary with job details (title, company, description, etc.)
            candidate_json: Dictionary with candidate profile information
            message_type: Type of message - 'linkedin_connection', 'linkedin_message', or 'email'
            tone: Tone of message - 'professional', 'friendly', or 'enthusiastic'
            keywords: Optional list of keywords to emphasize
            
        Returns:
            Dictionary containing:
                - message_type: Type of message
                - subject: Subject line (for emails) or connection note
                - body: Main message body
                - short_version: Shortened version for connection requests
                - tips: List of personalization tips
        """
        # Extract relevant info
        job_title = job_data.get('title', 'Position')
        company = job_data.get('company', 'the company')
        location = job_data.get('location', '')
        
        candidate_name = candidate_json.get('name', 'there')
        candidate_skills = candidate_json.get('skills', [])
        candidate_experience = candidate_json.get('experience', [])
        
        # Build the prompt based on message type
        if message_type == "linkedin_connection":
            max_length = 300
            prompt_template = f"""Create a SHORT and PERSONAL LinkedIn connection request message.

STRICT REQUIREMENTS:
- Maximum {max_length} characters (LinkedIn limit)
- Mention ONE specific common interest or relevant skill
- Reference the company: {company}
- Use a {tone} tone
- Be genuine and specific, not generic

CANDIDATE INFO:
Name: {candidate_name}
Top Skills: {', '.join(candidate_skills[:3]) if candidate_skills else 'Not specified'}

JOB INFO:
Title: {job_title}
Company: {company}
Location: {location}

Return JSON with:
{{
    "subject": "Short connection note/reason",
    "body": "The actual connection request message (under {max_length} chars)",
    "tips": ["personalization tip 1", "personalization tip 2"]
}}
"""
        elif message_type == "linkedin_message":
            max_length = 2000
            prompt_template = f"""Create a personalized LinkedIn InMail or direct message.

REQUIREMENTS:
- Maximum {max_length} characters
- Clear expression of interest in the role
- Highlight 2-3 relevant skills/experiences
- Include a call-to-action
- Use a {tone} tone
- Be authentic and specific

CANDIDATE INFO:
Name: {candidate_name}
Skills: {', '.join(candidate_skills[:5]) if candidate_skills else 'Not specified'}
Recent Experience: {candidate_experience[0].get('title', '') if candidate_experience else 'Not specified'}

JOB INFO:
Title: {job_title}
Company: {company}
Location: {location}
{f"Key Skills Needed: {', '.join(keywords)}" if keywords else ''}

Return JSON with:
{{
    "subject": "Message subject/opening",
    "body": "The full message",
    "tips": ["personalization tip 1", "personalization tip 2", "personalization tip 3"]
}}
"""
        else:  # email
            prompt_template = f"""Create a professional email for a job opportunity.

REQUIREMENTS:
- Professional email format with greeting and signature
- Clear subject line
- Express genuine interest and relevant qualifications
- Highlight 3-4 key skills/experiences that match the role
- Include availability for discussion
- Use a {tone} tone

CANDIDATE INFO:
Name: {candidate_name}
Skills: {', '.join(candidate_skills[:7]) if candidate_skills else 'Not specified'}
Experience: {json.dumps(candidate_experience[:2], indent=2) if candidate_experience else 'Not specified'}

JOB INFO:
Title: {job_title}
Company: {company}
Location: {location}
{f"Key Requirements: {', '.join(keywords)}" if keywords else ''}

Return JSON with:
{{
    "subject": "Professional email subject line",
    "body": "The complete email body with greeting and closing",
    "tips": ["personalization tip 1", "personalization tip 2", "personalization tip 3"]
}}
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt_template,
                config={
                    "response_mime_type": "application/json",
                }
            )
            
            result = json.loads(response.text)
            
            # Add short version for connection requests
            if message_type == "linkedin_connection":
                body = result.get("body", "")
                if len(body) > 300:
                    result["short_version"] = body[:297] + "..."
                else:
                    result["short_version"] = body
            
            result["message_type"] = message_type
            result["tone"] = tone
            
            return result
            
        except Exception as e:
            print(f"Error generating message: {e}")
            # Fallback to basic template
            return self._fallback_message(job_data, candidate_json, message_type, tone)
    
    def _fallback_message(
        self,
        job_data: Dict,
        candidate_json: Dict,
        message_type: str,
        tone: str
    ) -> Dict:
        """Fallback message template when API fails"""
        job_title = job_data.get('title', 'Position')
        company = job_data.get('company', 'your company')
        candidate_name = candidate_json.get('name', 'there')
        
        if message_type == "linkedin_connection":
            body = f"Hi! I'm interested in the {job_title} role at {company}. Would love to connect and learn more about the opportunity."
            return {
                "message_type": message_type,
                "subject": "Connection request about opportunity",
                "body": body,
                "short_version": body,
                "tips": ["Personalize with specific skills", "Mention mutual connections if any"]
            }
        elif message_type == "linkedin_message":
            body = f"""Hello,

I came across the {job_title} position at {company} and am very interested in learning more. My background in [mention relevant skill] aligns well with the requirements.

Would you be available for a brief conversation about the role?

Best regards,
{candidate_name}"""
            return {
                "message_type": message_type,
                "subject": f"Inquiry about {job_title} position",
                "body": body,
                "tips": ["Add specific skills", "Mention relevant experience", "Include portfolio link"]
            }
        else:  # email
            body = f"""Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company}.

With my experience in [mention relevant skills], I believe I would be a strong fit for this role. I am particularly excited about [mention something specific about the company/role].

I would welcome the opportunity to discuss how my skills and experience align with your needs. I am available for a conversation at your convenience.

Thank you for considering my application.

Best regards,
{candidate_name}"""
            return {
                "message_type": message_type,
                "subject": f"Application for {job_title} Position",
                "body": body,
                "tips": ["Customize with your specific skills", "Research the company", "Include relevant achievements"]
            }


def generate_reach_out_message(
    job_data: Dict,
    candidate_json: Dict,
    message_type: str = "linkedin_connection",
    tone: str = "professional",
    keywords: Optional[List[str]] = None
) -> Dict:
    """
    Convenience function to generate a reach out message.
    
    Args:
        job_data: Job information dictionary
        candidate_json: Candidate profile dictionary
        message_type: Type of message to generate
        tone: Tone of the message
        keywords: Optional keywords to emphasize
        
    Returns:
        Generated message dictionary
    """
    generator = ReachOutGenerator()
    return generator.generate_message(
        job_data=job_data,
        candidate_json=candidate_json,
        message_type=message_type,
        tone=tone,
        keywords=keywords
    )


if __name__ == "__main__":
    # Test with sample data
    sample_job = {
        "title": "Senior Python Developer",
        "company": "Tech Corp",
        "location": "Berlin, Germany",
        "description": "Looking for an experienced Python developer..."
    }
    
    sample_candidate = {
        "name": "John Doe",
        "skills": ["Python", "Django", "AWS", "Docker"],
        "experience": [
            {"title": "Software Engineer", "company": "Previous Corp"}
        ]
    }
    
    # Test different message types
    for msg_type in ["linkedin_connection", "linkedin_message", "email"]:
        print(f"\n{'='*50}")
        print(f"Testing {msg_type}")
        print(f"{'='*50}")
        result = generate_reach_out_message(
            job_data=sample_job,
            candidate_json=sample_candidate,
            message_type=msg_type,
            tone="professional"
        )
        print(json.dumps(result, indent=2))
