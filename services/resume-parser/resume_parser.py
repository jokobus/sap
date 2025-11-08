import os
import json
from typing import Tuple, List

import fitz
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError
from pydantic import ValidationError
from resume_schema import Resume

load_dotenv()
client = genai.Client()

MODEL = "gemini-2.0-flash" #good balance
# MODEL = "gemini-2.0-flash-lite" # not got social links
# MODEL = "gemini-2.5-flash-lite"
# MODEL = "gemini-2.5-flash"

RESUMES_ROOT = os.path.abspath("services/resume-parser/sample-resumes")

PROMPT = """
            You are an expert resume-parser-API endpoint. Your sole task is to analyze the resume text provided below and produce a single, valid JSON object that conforms *exactly* to the provided JSON Schema.

            ### INSTRUCTIONS ###
            1.  **Date Format:** For all date fields (start/end year), use a four-digit **integer** (e.g., 2024) or the literal string **"Present"**.
            2.  **Required Data:** The fields 'name', 'email', and 'education' must be extracted.
            3.  **Skills:** Categorize all skills found into the 'skills' list using the 'SkillCategory' structure.
            4.  **Links:** All URL fields (e.g., social links, project links) must be valid URI strings starting with a protocol (e.g., 'https://').
            5.  **Description Points:** Break down experience, project, and responsibility descriptions into bullet points.

            ### RESUME DATA TO PARSE ###
            ---START OF RESUME TEXT---
            {resume_text}
            ---END OF RESUME TEXT---
        """

app = FastAPI()

def extract_text_and_links_from_pdf(path: str) -> Tuple[str, List[str]]:
    final_path = os.path.join(os.getcwd(), path)
    doc = fitz.open(final_path)
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


def model_response(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": Resume,
        },
    )
    return response.text

@app.post("/parse")
async def parse_resume(file_path: str = Query(..., alias="file")):
    dest = os.path.abspath(os.path.join(RESUMES_ROOT, file_path.lstrip("/")))


    try:
        text, links = extract_text_and_links_from_pdf(dest)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read or parse PDF: {e}")
        
    resume_content = text + "\n Links: " + "\n".join(links)
    prompt = PROMPT.format(resume_text=resume_content)


    try:
        resp = model_response(prompt)
    except APIError as e:
        error_detail = "API call failed (e.g., Rate Limit Exceeded, Invalid Key, or Server Error)."
        if "rate limit" in str(e).lower() or "authentication" in str(e).lower():
            error_detail = f"Gemini API Error: {e}"
        raise HTTPException(status_code=503, detail=error_detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during API call: {e}")

    # Pydantic Validation and JSON Parsing
    try:
        validated_resume = Resume.model_validate_json(resp)
        # data = validated_resume.model_dump() # gave error: Object of type AnyUrl is not JSON serializable
        return validated_resume

    except (json.JSONDecodeError, ValidationError) as e:
        return JSONResponse(
            content={
                "error": "Model response validation failed (LLM output does not match schema).",
                "llm_output": resp,
                "validation_error": str(e)
            }, 
            status_code=500
        )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
