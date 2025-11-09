import os
import json
from typing import Tuple, List

import fitz
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import uvicorn
# from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError
from pydantic import ValidationError
from services.linkedin_profile_scraper.linkedin_schema import LinkedInProfile
from services.utils import to_serializable

# load_dotenv()
# client = genai.Client()

MODEL = "gemini-2.0-flash" #good balance
# MODEL = "gemini-2.0-flash-lite" # not got social links
# MODEL = "gemini-2.5-flash-lite"
# MODEL = "gemini-2.5-flash"


PROMPT = """
            You are an expert LinkedIn-profile-parser. Your sole task is to analyze the LinkedIn profile text provided below and produce a single, valid JSON object that conforms *exactly* to the provided LinkedInProfile Pydantic schema.

            ### INSTRUCTIONS ###
            1. **Date Format:** For all date fields (start/end year), use a four-digit **integer** (e.g., 2024) or the literal string **"Present"**. For months, use integers 1–12 if available.
            2. **Required Data:** The fields 'name' and 'education' must be extracted.
            3. **Skills:** Include all top skills in the 'top_skills' list. Include any honors or awards in 'honors_awards'.
            4. **Links:** All URL fields (profile_url, project links, credential_url, publication URLs, other_links) must be valid URI strings starting with a protocol (e.g., 'https://').
            5. **Descriptions:** Break down experience, project, certification, volunteer, and publication descriptions into bullet points.
            6. **Optional Fields:** Populate optional fields (headline, location, about, languages, recommendations_count) when available; omit them or leave empty lists if not present.

            ### LINKEDIN PROFILE DATA TO PARSE ###
            ---START OF LINKEDIN PROFILE TEXT---
            {linkedin_text}
            ---END OF LINKEDIN PROFILE TEXT---
        """

def extract_text_and_links_from_pdf(file_bytes: bytes) -> Tuple[str, List[str]]:
    # final_path = os.path.join(os.getcwd(), path)
    # doc = fitz.open(file_bytes)
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    parts = []
    urls = set()
    for page in doc:
        t = page.get_text().strip()
        if t:
            parts.append(t)
        links = page.get_links()
        for link in links:
            if link.get("kind") == fitz.LINK_URI and link.get("uri"):
                urls.add(link["uri"])
    return "\n".join(parts).strip(), sorted(urls)


def model_response(prompt: str, client) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": LinkedInProfile,
        },
    )
    return response.text


async def parse_linkedin(file_bytes, client):
    try:
        text, links = extract_text_and_links_from_pdf(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read or parse PDF: {e}")

    linkedin_content = text + "\n Links: " + "\n".join(links)
    prompt = PROMPT.format(linkedin_text=linkedin_content)

    resp = model_response(prompt, client)

    validated_resume = LinkedInProfile.model_validate_json(resp)
    # data = validated_resume.model_dump() # gave error: Object of type AnyUrl is not JSON serializable
    data = to_serializable(validated_resume)
    print("\n\nFrom LINKEDIN: ", data, "\n\n")
    return data