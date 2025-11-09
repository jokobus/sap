import os
import requests
from requests.exceptions import RequestException
from typing import Tuple, List, Dict, Any, Optional
from pydantic import AnyUrl, ValidationError
from collections import defaultdict
from pydantic import BaseModel, AnyUrl
import logging
import json
from dotenv import load_dotenv
from services.utils import to_serializable

load_dotenv()
# Import your existing schema definitions
# We assume resume_schema.py is in the parent directory or accessible in PYTHONPATH
try:
    from services.resume_parser.resume_schema import Project, SkillCategory
except ImportError:
    # Fallback for relative import if running as a script
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from services.resume_parser.resume_schema import Project, SkillCategory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
API_URL = "https://api.github.com"

# --- IMPORTANT ---
# This script REQUIRES a GitHub Personal Access Token (PAT) for API authentication.
# Without it, you will hit rate limits very quickly.
#
# 1. Create a token at: https://github.com/settings/tokens (use "Classic")
# 2. Give it "repo" and "user" scopes.
# 3. Add it to your .env file as:
#    GITHUB_API_TOKEN="ghp_..."
#
# This script (and dotenv) will automatically load it.
GITHUB_TOKEN = os.getenv("GITHUB_API_TOKEN")

if not GITHUB_TOKEN:
    logging.warning(
        "GITHUB_API_TOKEN environment variable not set. "
        "API calls will be unauthenticated and may hit rate limits."
    )

def _get_auth_headers() -> Dict[str, str]:
    """Returns the authentication headers for the GitHub API."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers

def _fetch_github_data(url: str) -> Optional[Any]:
    """Helper function to fetch data from a GitHub API URL."""
    try:
        response = requests.get(url, headers=_get_auth_headers())
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses
        return response.json()
    except RequestException as e:
        logging.error(f"Failed to fetch data from {url}: {e}")
        return None

async def parse_github_profile(username: str) -> Tuple[List[Project], List[SkillCategory], List[AnyUrl]]:
    """
    Fetches a user's GitHub profile data and maps it to the Resume schema.
    
    Args:
        username: The GitHub username.
        
    Returns:
        A tuple containing:
        - list[Project]: A list of the user's repositories as Project objects.
        - list[SkillCategory]: A list containing a SkillCategory for languages.
        - list[AnyUrl]: A list containing the user's GitHub profile URL.
    """
    
    projects: List[Project] = []
    social_links: List[AnyUrl] = []
    language_bytes: Dict[str, int] = defaultdict(int)

    # --- 1. Get User Profile (for social link) ---
    user_url = f"{API_URL}/users/{username}"
    user_data = _fetch_github_data(user_url)
    
    if not user_data:
        logging.error(f"Could not fetch user profile for {username}")
        return [], [], [] # Return empty lists if user not found
        
    try:
        if 'html_url' in user_data:
            social_links.append(AnyUrl(user_data['html_url']))
    except ValidationError as e:
        logging.warning(f"Invalid social URL found for user {username}: {user_data.get('html_url')} - {e}")

    # --- 2. Get Repositories (for Projects and Skills) ---
    repos_url = user_data.get('repos_url')
    if not repos_url:
        logging.error(f"Could not find repos_url for {username}")
        return [], [], social_links

    repos_data = _fetch_github_data(f"{repos_url}?per_page=100") # Get up to 100 repos
    
    if not repos_data:
        logging.info(f"No repositories found or failed to fetch for {username}")
        return [], [], social_links

    for repo in repos_data:
        if repo.get('fork'):
            continue  # Skip forked repositories
        
        # Map to Project schema
        try:
            # Your schema's `description_points` is a list.
            # The API's `description` is a single string.
            # We'll add it as a single-item list.
            desc_points = [repo['description']] if repo.get('description') else []
            
            project = Project(
                name=repo.get('name', 'N/A'),
                description_points=desc_points,
                link=AnyUrl(repo.get('html_url', ''))
            )
            projects.append(project)
        except ValidationError as e:
            logging.warning(f"Failed to validate project {repo.get('name')}: {e}")
            continue

        # --- 3. Get Languages for each Repo (for Skills) ---
        languages_url = repo.get('languages_url')
        if languages_url:
            lang_data = _fetch_github_data(languages_url)
            if lang_data:
                for lang, byte_count in lang_data.items():
                    language_bytes[lang] += byte_count

    # --- 4. Format Skills ---
    # Create one SkillCategory for all programming languages
    skills: List[SkillCategory] = []
    if language_bytes:
        # Sort languages by bytes, most used first
        sorted_languages = sorted(language_bytes.items(), key=lambda item: item[1], reverse=True)
        language_names = [lang for lang, count in sorted_languages]
        
        skills.append(
            SkillCategory(
                category_name="Programming Languages (from GitHub)",
                skills=language_names
            )
        )

    logging.info(f"Successfully parsed GitHub profile for {username}. "
                 f"Found {len(projects)} projects and {len(language_bytes)} languages.")

    output = {"projects": projects, "skills": skills, "social_links": social_links}

    final_json = json.dumps(to_serializable(output), indent=2)
    print("\nFrom GITHUB json:\n", final_json)

    return final_json

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    import json
    
    # Load .env file (e.g., for GITHUB_API_TOKEN)
    load_dotenv()
    
    async def main():
        # Test with a well-known GitHub user
        TEST_USERNAME = "torvalds" 
        logging.info(f"--- Testing GitHub parser for: {TEST_USERNAME} ---")
        response = await parse_github_profile(TEST_USERNAME)
        # print(response)
        data = json.loads(response)

        projects = data.get("projects", [])
        skills = data.get("skills", [])
        social_links = data.get("social_links", [])

        print("\n--- 🔗 SOCIAL LINKS ---")
        print(json.dumps([str(url) for url in social_links], indent=2))
        
        print("\n--- 🛠️ SKILLS ---")
        print(json.dumps([skill.model_dump() for skill in skills], indent=2))
        
        print(f"\n--- 📂 PROJECTS (First 5) ---")
        print(json.dumps([proj.model_dump(mode='json') for proj in projects], indent=2))
        print(f"\n... and {len(projects) - 5} more projects.")

    # Note: In Python 3.6 you might need `asyncio.get_event_loop().run_until_complete(main())`
    asyncio.run(main())