# Cover Letter Generator Agent

An AI-powered agent that automatically generates personalized cover letters based on job descriptions and your resume using Google's Gemini API.

## Features

- 📄 Reads job descriptions from text files
- 📋 Parses resume data from JSON format
- 🤖 Uses Google Gemini AI to generate personalized cover letters
- ✍️ Creates professional, tailored content matching job requirements
- 💾 Automatically saves output with timestamp

## Prerequisites

- Python 3.7 or higher
- **Google Gemini API key** (see setup instructions below)
- Internet connection

### Getting Your Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"** or **"Get API Key"**
4. Copy the generated key (format: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)
5. Keep it secure - treat it like a password!

**Note**: The code `RL9B-NC4E-PGRU-D7QP` you provided appears to be a different type of code. You'll need to get a proper Gemini API key from the link above.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements_coverlet.txt
```

Or install directly:
```bash
pip install google-generativeai
```

## Configuration

### Set Your API Key

You have two options:

**Option 1: Environment Variable (Recommended)**
```bash
export GOOGLE_API_KEY="your-actual-api-key-here"
./venv/bin/python cover_letter_agent.py
```

**Option 2: Edit the Script**
Open `cover_letter_agent.py` and replace the placeholder API key:
```python
API_KEY = "your-actual-api-key-here"
```

## Usage

### Quick Start

Once your API key is configured, run the script:
```bash
./venv/bin/python cover_letter_agent.py
```

Or with environment variable:
```bash
export GOOGLE_API_KEY="your-api-key"
./venv/bin/python cover_letter_agent.py
```

The agent will:
1. Read your job description from `job_description.txt`
2. Parse your resume from `Shishir_Sunar.resume.json`
3. Generate a personalized cover letter using AI
4. Display the cover letter in the console
5. Save it to a timestamped file (e.g., `cover_letter_20251108_143022.txt`)

### File Requirements

Make sure you have these files in the same directory:
- `job_description.txt` - The job posting you're applying for
- `Shishir_Sunar.resume.json` - Your resume in JSON Resume format

## How It Works

1. **Initialization**: The agent connects to Google's Gemini API using the provided API key
2. **Data Reading**: Reads and parses the job description and resume
3. **Context Building**: Creates a comprehensive summary of your qualifications
4. **AI Generation**: Sends a structured prompt to Gemini AI with:
   - Job requirements and description
   - Your relevant experience and skills
   - Instructions for professional formatting
5. **Output**: Generates a 3-4 paragraph cover letter that:
   - Addresses specific job requirements
   - Highlights relevant experience
   - Shows enthusiasm and fit
   - Uses professional language

## Output Format

The generated cover letter includes:
- Professional greeting
- Strong opening paragraph
- Body paragraphs highlighting relevant experience
- Closing paragraph expressing interest
- Professional sign-off

Example output filename: `cover_letter_20251108_143022.txt`

## Customization

You can modify the agent by editing `cover_letter_agent.py`:

### Change API Key
```python
API_KEY = "your-api-key-here"
```

### Change Input Files
```python
JOB_DESCRIPTION_FILE = "your_job_description.txt"
RESUME_FILE = "your_resume.json"
```

### Adjust Output Location
```python
OUTPUT_FILE = "custom_name.txt"
```

### Customize Prompt
Edit the `generate_cover_letter()` method to adjust the AI instructions.

## Resume Format

The agent expects a JSON Resume format (schema v1.0.0). Your resume should include:
- `basics`: Name, contact information
- `education`: Degrees and institutions
- `work`: Work experience
- `skills`: Technical and soft skills
- `projects`: Notable projects
- `certificates`: Certifications

## Troubleshooting

### Import Error
If you get "Import could not be resolved":
```bash
pip install --upgrade google-generativeai
```

### API Error
- Check your API key is correct
- Ensure you have internet connection
- Verify the API key has Gemini access enabled

### File Not Found
- Ensure `job_description.txt` and `Shishir_Sunar.resume.json` are in the same directory as the script
- Check file names match exactly (case-sensitive on Linux/Mac)

## Example Output

The agent generates professional cover letters like:

```
Dear Hiring Manager,

I am writing to express my strong interest in the Working Student (m/f/d) – AI Developer 
position at Dassault Systèmes' 3DEXCITE brand in Munich. As a current Master's student in 
Informatics at the Technical University of Munich with extensive experience in AI development 
and computer vision, I am excited about the opportunity to contribute to your team's mission 
of implementing software components for Design Validation and Marketing Experiences.

[... continues with relevant experience and qualifications ...]
```

## License

This project is provided as-is for personal use.

## Support

For issues or questions, please refer to the Google Gemini API documentation:
https://ai.google.dev/docs

---

**Note**: Remember to keep your API key secure and never commit it to public repositories!
