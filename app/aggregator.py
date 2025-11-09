from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError
from pydantic import ValidationError
from services.resume_parser.resume_parser import parse_resume
from services.linkedin_profile_scraper.linkedin_scraper import parse_linkedin
from services.github_scraper.github_scraper import parse_github_profile
from aggregator_schema import FinalSchema as AggregatedProfile
from services.utils import to_serializable
import asyncio

load_dotenv()
client = genai.Client()

MODEL = "gemini-2.0-flash" #good balance
# MODEL = "gemini-2.0-flash-lite" # not got social links
# MODEL = "gemini-2.5-flash-lite"
# MODEL = "gemini-2.5-flash"

resume_file_pth = "sample-resumes/sample_resume_1.pdf"
linkedin_file_pth = "sample-linkedin-profiles/sample_linkedin_1.pdf"
github_username = "BhavikOstwal"

PROMPT = """
                You are an expert data aggregation service. Your sole task is to merge the three JSON inputs below (resume, LinkedIn, GitHub) into a **single, valid JSON object** conforming *exactly* to the `FinalSchema`.

                ### Core Requirements ###

                1.  **Strict Schema:** The output *must* perfectly validate against `FinalSchema`.
                2.  **Deduplicate & Merge:** Intelligently identify and merge duplicate entries (for `experience`, `education`, `projects`, etc.) into single objects.
                3.  **Enrich Data:** When merging, populate the single object with the most complete data from all sources (e.g., resume descriptions, LinkedIn dates).
                4.  **Track Sources:** This is critical. For *every* item (`UnifiedExperience`, `SkillCategory`, `UnifiedProject`, etc.), you *must* populate its `source` list (e.g., `["resume", "linkedin"]`).
                5.  **Aggregate Skills:** Combine all skills from all sources, deduplicate them, and group them into `SkillCategory`, tracking their sources.
                6.  **Metadata:** Populate the top-level `data_sources` list.

                Your output must be **only** the final JSON object, with no conversational text.

                ### Data Inputs ###

                ---RESUME JSON---
                {resume_json}
                ---END RESUME---

                ---LINKEDIN JSON---
                {linkedin_json}
                ---END LINKEDIN---

                ---GITHUB JSON---
                {github_json}
                ---END GITHUB---
            """

def model_response(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": AggregatedProfile,
        },
    )
    return response.text


async def parse_all(resume, linkedin, github_name) -> AggregatedProfile:

    resume_json = await parse_resume(resume, client)
    linkedin_json = await parse_linkedin(linkedin, client)
    github_json = await parse_github_profile(github_name)
    prompt = PROMPT.format(resume_json=resume_json, linkedin_json=linkedin_json, github_json=github_json)

    resp = model_response(prompt)

    # Pydantic Validation and JSON Parsing
    validated_output = AggregatedProfile.model_validate_json(resp)
    # data = validated_resume.model_dump() # gave error: Object of type AnyUrl is not JSON serializable
    data = to_serializable(validated_output)
    print("\n\nFrom AGGREGATOR: ", data, "\n\n")
    return data


# resp = asyncio.run(parse_all("aarya.pdf", "pro.pdf", "dnfy502"))
