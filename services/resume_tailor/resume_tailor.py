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
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.lib.utils import simpleSplit
    except Exception as e:
        raise RuntimeError("reportlab is required to create PDF: pip install reportlab") from e

    c = canvas.Canvas(out_pdf, pagesize=A4)
    width, height = A4
    # Layout parameters
    margin = 18 * mm
    gutter = 8 * mm
    sidebar_w = 58 * mm
    main_w = width - margin * 2 - sidebar_w - gutter

    # Colors and fonts
    accent = colors.HexColor('#0B63A7')
    name_font = 'Helvetica-Bold'
    header_font = 'Helvetica-Bold'
    body_font = 'Helvetica'

    # Helper: page management
    def new_page():
        c.showPage()

    # Helper: draw wrapped text using simpleSplit
    def draw_wrapped(text, x, y, max_width, font_name, font_size, leading=14):
        lines = simpleSplit(text or '', font_name, font_size, max_width)
        for ln in lines:
            c.setFont(font_name, font_size)
            c.drawString(x, y, ln)
            y -= leading
            if y < margin:
                new_page()
                y = height - margin
        return y

    basics = resume.get('basics', {})

    # Header: name and title
    header_y = height - margin
    c.setFillColor(accent)
    c.rect(margin, header_y - 28, width - margin * 2, 28, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(name_font, 16)
    c.drawString(margin + 6, header_y - 22, basics.get('name', ''))
    c.setFont(body_font, 10)
    title = basics.get('label') or basics.get('headline') or ''
    c.drawString(margin + 6, header_y - 36 + 6, title)

    # Sidebar background
    sidebar_x = margin
    sidebar_y = header_y - 40
    c.setFillColor(colors.whitesmoke)
    c.rect(sidebar_x, margin, sidebar_w, sidebar_y - margin, fill=1, stroke=0)

    # Contact info in sidebar
    contact_x = sidebar_x + 8
    contact_y = sidebar_y - 12
    c.setFillColor(colors.black)
    c.setFont(header_font, 10)
    c.drawString(contact_x, contact_y, 'Contact')
    contact_y -= 14
    c.setFont(body_font, 9)
    contact_lines = []
    if basics.get('email'):
        contact_lines.append(basics.get('email'))
    if basics.get('phone'):
        contact_lines.append(basics.get('phone'))
    loc = basics.get('location', {})
    if loc.get('address'):
        contact_lines.append(loc.get('address'))
    for ln in contact_lines:
        contact_y = draw_wrapped(ln, contact_x, contact_y, sidebar_w - 12, body_font, 8, leading=11)
        contact_y -= 4

    # Skills in sidebar
    skills = [s.get('name') for s in resume.get('skills', []) if s.get('name')]
    if skills:
        contact_y -= 6
        c.setFont(header_font, 10)
        c.drawString(contact_x, contact_y, 'Skills')
        contact_y -= 14
        c.setFont(body_font, 8)
        skills_text = ', '.join(skills[:40])
        contact_y = draw_wrapped(skills_text, contact_x, contact_y, sidebar_w - 12, body_font, 8, leading=11)

    # Projects/Certificates small list in sidebar
    projects = resume.get('projects', [])
    if projects:
        contact_y -= 6
        c.setFont(header_font, 10)
        c.drawString(contact_x, contact_y, 'Projects')
        contact_y -= 14
        c.setFont(body_font, 8)
        for p in projects[:6]:
            contact_y = draw_wrapped(p.get('name',''), contact_x, contact_y, sidebar_w - 12, body_font, 8, leading=11)
            contact_y -= 4

    # Main column: experience, education, projects details
    main_x = margin + sidebar_w + gutter
    y = height - margin - 50
    c.setFillColor(colors.black)

    def write_heading(text):
        nonlocal y
        c.setFont(header_font, 12)
        c.setFillColor(accent)
        c.drawString(main_x, y, text)
        y -= 16
        c.setFillColor(colors.black)

    # Work Experience
    works = resume.get('work', [])
    if works:
        write_heading('Work Experience')
        for w in works:
            pos = f"{w.get('position','')} — {w.get('name','')} ({w.get('startDate','')}-{w.get('endDate','Present')})"
            c.setFont(name_font, 10)
            c.drawString(main_x, y, pos)
            y -= 14
            summary = w.get('summary','')
            if summary:
                y = draw_wrapped(summary, main_x, y, main_w, body_font, 9, leading=12)
                y -= 6
            # bullets
            for b in w.get('highlights', [])[:6]:
                bullet = '• ' + b
                y = draw_wrapped(bullet, main_x + 6, y, main_w - 6, body_font, 9, leading=12)
                y -= 2
            if y < margin + 60:
                new_page()
                y = height - margin

    # Education
    eds = resume.get('education', [])
    if eds:
        write_heading('Education')
        for e in eds:
            edu = f"{e.get('studyType','')} in {e.get('area','')} — {e.get('institution','')} ({e.get('startDate','')}-{e.get('endDate','')})"
            y = draw_wrapped(edu, main_x, y, main_w, body_font, 9, leading=12)
            y -= 6

    # Projects (expanded)
    if projects:
        write_heading('Projects')
        for p in projects[:8]:
            title = f"{p.get('name','')} — {p.get('roles','') or ''}"
            c.setFont(name_font, 9)
            c.drawString(main_x, y, title)
            y -= 12
            summary = p.get('summary','')
            y = draw_wrapped(summary, main_x, y, main_w, body_font, 9, leading=12)
            y -= 6

    c.save()


def main() -> None:
    API_KEY = os.environ.get('GOOGLE_API_KEY')
    if not API_KEY:
        print('Please set GOOGLE_API_KEY environment variable and retry.')
        return

    client = genai.Client(api_key=API_KEY)

    with open('job_description.txt', 'r', encoding='utf-8') as f:
        job = f.read()

    with open('Shishir_Sunar.resume.json', 'r', encoding='utf-8') as f:
        base_resume = json.load(f)

    # Check for GitHub analysis
    github_context = ""
    try:
        github_files = sorted([f for f in os.listdir('.') if f.startswith('github_portfolio_analysis_')])
        if github_files:
            with open(github_files[-1], 'r') as f:
                github_data = json.load(f)
                analysis = github_data.get('analysis', {})
                github_context = "\n\nGITHUB PORTFOLIO:\n" + json.dumps({
                    'matched_projects': analysis.get('matched_projects', [])[:3],
                    'technical_summary': analysis.get('technical_summary', '')
                })
    except:
        pass

    # Build a compact prompt telling the model to output only JSON resume
    prompt = (
        "Given the job posting below, tailor the candidate's resume to highlight the most relevant "
        "experience, skills and projects. Output strictly a single JSON object in JSON Resume schema (basics, work, education, skills, projects, certificates). "
        "Do NOT output any explanation or extra text.\n\n"
        "JOB:\n" + job + "\n\nCANDIDATE_BASE:\n" + json.dumps(base_resume) + github_context + "\n\n"
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
