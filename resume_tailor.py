#!/usr/bin/env python3
"""Tailored Resume generator + PDF converter

Usage:
  export GOOGLE_API_KEY="your-key"
  ./venv/bin/python resume_tailor.py

Produces:
  - tailored_resume.json
  - tailored_resume.pdf
"""

import json
import os
from datetime import datetime
from google import genai
from typing import Any


def safe_extract_json(text: str) -> str:
    """Try to extract JSON substring from model output."""
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end < start:
        return text
    return text[start:end+1]


def resume_to_pdf(resume: dict, out_pdf: str) -> None:
    """Render a simple resume to PDF using reportlab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception as e:
        raise RuntimeError("reportlab is required to create PDF: pip install reportlab") from e

    c = canvas.Canvas(out_pdf, pagesize=A4)
    width, height = A4
    margin = 50
    y = height - margin
    line_height = 14

    def write(line: str, bold=False):
        nonlocal y
        if y < margin:
            c.showPage()
            y = height - margin
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 11 if bold else 10)
        c.drawString(margin, y, line)
        y -= line_height

    basics = resume.get('basics', {})
    write(basics.get('name', ''))
    contact = f"{basics.get('email','')} | {basics.get('phone','')} | {basics.get('location',{}).get('address','')}"
    write(contact)
    write('')

    # Education
    eds = resume.get('education', [])
    if eds:
        write('Education', bold=True)
        for e in eds:
            write(f"{e.get('studyType','')} in {e.get('area','')} — {e.get('institution','')} ({e.get('startDate','')}-{e.get('endDate','')})")
        write('')

    # Experience
    works = resume.get('work', [])
    if works:
        write('Work Experience', bold=True)
        for w in works:
            write(f"{w.get('position','')} — {w.get('name','')} ({w.get('startDate','')}-{w.get('endDate','Present')})")
            summary = w.get('summary','')
            if summary:
                # split summary into shorter lines
                for chunk in summary.split('\n'):
                    write('  ' + chunk)
        write('')

    # Skills
    skills = [s.get('name') for s in resume.get('skills', []) if s.get('name')]
    if skills:
        write('Skills', bold=True)
        write(', '.join(skills))
        write('')

    # Projects
    projects = resume.get('projects', [])
    if projects:
        write('Projects', bold=True)
        for p in projects[:6]:
            write(f"- {p.get('name','')}: {p.get('summary','')}")
        write('')

    c.save()


def main() -> None:
    API_KEY = "AIzaSyCdpcLoI53VCunQagRNfQoZjvIALFANHEY"
    if not API_KEY:
        print('Please set GOOGLE_API_KEY environment variable and retry.')
        return

    client = genai.Client(api_key=API_KEY)

    with open('job_description.txt', 'r', encoding='utf-8') as f:
        job = f.read()

    with open('Shishir_Sunar.resume.json', 'r', encoding='utf-8') as f:
        base_resume = json.load(f)

    # Build a compact prompt telling the model to output only JSON resume
    prompt = (
        "Given the job posting below, tailor the candidate's resume to highlight the most relevant "
        "experience, skills and projects. Output strictly a single JSON object in JSON Resume schema (basics, work, education, skills, projects, certificates). "
        "Do NOT output any explanation or extra text.\n\n"
        "JOB:\n" + job + "\n\nCANDIDATE_BASE:\n" + json.dumps(base_resume) + "\n\n"
        "Return only the JSON object."
    )

    print('Requesting tailored resume from Gemini...')
    resp = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    text = resp.text

    # try to parse JSON
    json_text = safe_extract_json(text)
    try:
        tailored = json.loads(json_text)
    except Exception:
        # fallback: ask the raw text as a field
        tailored = {'error': 'failed_to_parse_model_output', 'raw': text}

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_out = f'tailored_resume_{timestamp}.json'
    pdf_out = f'tailored_resume_{timestamp}.pdf'

    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump(tailored, f, indent=2, ensure_ascii=False)
    print(f'Saved tailored JSON: {json_out}')

    # Convert to PDF if parsed
    if isinstance(tailored, dict) and 'error' not in tailored:
        try:
            resume_to_pdf(tailored, pdf_out)
            print(f'Saved PDF: {pdf_out}')
        except Exception as e:
            print('PDF conversion failed:', e)
    else:
        print('Skipping PDF conversion due to parse error. Check', json_out)


if __name__ == '__main__':
    main()
