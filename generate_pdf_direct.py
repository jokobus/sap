#!/usr/bin/env python3
"""Generate a PDF from a resume JSON without importing resume_tailor (avoids genai import).
This is a standalone runner that defines the same resume_to_pdf behavior and writes sample_resume_preview.pdf
"""
import json
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.utils import simpleSplit
except Exception as e:
    raise SystemExit("reportlab is required: pip install reportlab")

def resume_to_pdf(resume: dict, out_pdf: str) -> None:
    c = canvas.Canvas(out_pdf, pagesize=A4)
    width, height = A4
    margin = 18 * mm
    gutter = 8 * mm
    sidebar_w = 58 * mm
    main_w = width - margin * 2 - sidebar_w - gutter

    accent = colors.HexColor('#0B63A7')
    name_font = 'Helvetica-Bold'
    header_font = 'Helvetica-Bold'
    body_font = 'Helvetica'

    def new_page():
        c.showPage()

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
    header_y = height - margin
    c.setFillColor(accent)
    c.rect(margin, header_y - 28, width - margin * 2, 28, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont(name_font, 16)
    c.drawString(margin + 6, header_y - 22, basics.get('name', ''))
    c.setFont(body_font, 10)
    title = basics.get('label') or basics.get('headline') or ''
    c.drawString(margin + 6, header_y - 36 + 6, title)

    sidebar_x = margin
    sidebar_y = header_y - 40
    c.setFillColor(colors.whitesmoke)
    c.rect(sidebar_x, margin, sidebar_w, sidebar_y - margin, fill=1, stroke=0)

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

    skills = [s.get('name') for s in resume.get('skills', []) if s.get('name')]
    if skills:
        contact_y -= 6
        c.setFont(header_font, 10)
        c.drawString(contact_x, contact_y, 'Skills')
        contact_y -= 14
        c.setFont(body_font, 8)
        skills_text = ', '.join(skills[:40])
        contact_y = draw_wrapped(skills_text, contact_x, contact_y, sidebar_w - 12, body_font, 8, leading=11)

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
            for b in w.get('highlights', [])[:6]:
                bullet = '• ' + b
                y = draw_wrapped(bullet, main_x + 6, y, main_w - 6, body_font, 9, leading=12)
                y -= 2
            if y < margin + 60:
                new_page()
                y = height - margin

    eds = resume.get('education', [])
    if eds:
        write_heading('Education')
        for e in eds:
            edu = f"{e.get('studyType','')} in {e.get('area','')} — {e.get('institution','')} ({e.get('startDate','')}-{e.get('endDate','')})"
            y = draw_wrapped(edu, main_x, y, main_w, body_font, 9, leading=12)
            y -= 6

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


if __name__ == '__main__':
    candidates = [
        'tailored_resume_20251108_235714.json',
        'tailored_resume_20251108_235714.JSON',
        'Shishir_Sunar.resume.json',
    ]
    found = None
    for name in candidates:
        p = Path(name)
        if p.exists():
            found = p
            break
    if not found:
        print('No resume JSON found. Place one of:', candidates)
        raise SystemExit(1)
    with open(found, 'r', encoding='utf-8') as f:
        data = json.load(f)
    out = 'sample_resume_preview.pdf'
    resume_to_pdf(data, out)
    print('Saved', out)
