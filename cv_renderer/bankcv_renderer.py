"""BankCV-like PDF renderer using ReportLab.

This renderer maps important visual concepts from `bankcv.cls` (margins, header layout,
uppercase section headings with a rule, left sidebar for contact/skills/projects,
and main column for experience/education/projects) into ReportLab drawing calls.

Usage: import resume_to_pdf_bankcv or run `generate_bankcv_pdf.py`.
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from math import ceil


def resume_to_pdf_bankcv(resume: dict, out_pdf: str, sidebar_cols=3):
    c = canvas.Canvas(out_pdf, pagesize=A4)
    width, height = A4

    # BankCV default spacing (mapped from class file)
    margin_top = 25 * mm  # ~2.5cm
    margin_bottom = 20 * mm
    margin_left = 20 * mm
    margin_right = 20 * mm

    page_inner_w = width - margin_left - margin_right
    page_inner_h = height - margin_top - margin_bottom

    # Main column uses full page inner width (no sidebar)
    main_w = page_inner_w

    # Fonts and sizes
    name_font = 'Times-Bold'
    header_font = 'Times-Bold'
    body_font = 'Times-Roman'
    small_font = 'Times-Roman'

    name_size = 18
    header_size = 11
    section_size = 11
    body_size = 9
    small_size = 8

    accent = colors.HexColor('#0B63A7')
    rule_color = colors.black

    def draw_wrapped(text, x, y, max_w, font_name, font_size, leading=None):
        if not text:
            return y
        if leading is None:
            leading = font_size + 2
        lines = simpleSplit(str(text), font_name, font_size, max_w)
        for ln in lines:
            if y < margin_bottom + font_size:
                c.showPage()
                y = height - margin_top
            c.setFont(font_name, font_size)
            c.drawString(x, y, ln)
            y -= leading
        return y

    # Header center: name and contact line
    basics = resume.get('basics', {})
    name = basics.get('name', '')
    title = basics.get('label') or basics.get('headline') or ''

    header_y = height - margin_top + 10
    # Name
    c.setFont(name_font, name_size)
    c.drawCentredString(margin_left + page_inner_w / 2, header_y, name)
    # Contact line (dot separators like \cdot)
    contact_items = []
    if basics.get('location', {}).get('address'):
        contact_items.append(basics.get('location', {}).get('address'))
    if basics.get('phone'):
        contact_items.append(basics.get('phone'))
    if basics.get('email'):
        contact_items.append(basics.get('email'))
    if basics.get('profiles'):
        # some JSON resumes use profiles array
        for p in basics.get('profiles', []):
            u = p.get('url') or p.get('network') or None
            if u:
                contact_items.append(u)

    contact_line = ' \u00b7 '.join(contact_items) if contact_items else title
    c.setFont(small_font, small_size)
    c.drawCentredString(margin_left + page_inner_w / 2, header_y - (name_size + 6), contact_line)

    # Starting y position for main content (just below header)
    top_area_bottom = header_y - (name_size + 6) - 6
    header_extra_gap = 8  # add small extra space under the header line
    main_y = top_area_bottom - (6 + header_extra_gap)

    # Projects list (kept for main flow)
    projects = resume.get('projects', [])

    # Main column: sections with uppercase headings + rule (full width)
    mx = margin_left
    my = main_y

    # extra vertical gap between section underline and first content
    section_gap = 12  # small space under the section hline

    def write_section(title):
        nonlocal my
        # uppercase
        heading = str(title).upper()
        c.setFont(header_font, section_size)
        c.setFillColor(colors.black)
        c.drawString(mx, my, heading)
        # rule under
        rule_y = my - 3
        c.setStrokeColor(rule_color)
        c.setLineWidth(0.5)
        c.line(mx, rule_y, mx + main_w, rule_y)
        my = rule_y - section_gap

    # Work Experience
    works = resume.get('work', [])
    if works:
        write_section('Work Experience')
        c.setFont(body_font, body_size)
        for w in works:
            # Line 1: Company (left, bold) | Location (right, bold)
            company = w.get('name', '')
            location_val = w.get('location', '')
            if isinstance(location_val, dict):
                loc_parts = [
                    location_val.get('city') or location_val.get('town') or None,
                    location_val.get('region') or location_val.get('state') or None,
                    location_val.get('country') or location_val.get('countryCode') or None,
                ]
                location = ", ".join([p for p in loc_parts if p])
            else:
                location = str(location_val) if location_val else ''

            c.setFont('Times-Bold', body_size)
            if company:
                c.drawString(mx, my, company)
            if location:
                c.drawRightString(mx + main_w, my, location)
            my -= body_size + 2

            # Line 2: Position (left, italic) | Dates (right, italic)
            position = w.get('position', '')
            start = w.get('startDate', '') or ''
            end = w.get('endDate', '') or ''
            dates = f"{start} — {end}".strip()
            c.setFont('Times-Italic', body_size)
            if position:
                c.drawString(mx, my, position)
            if dates:
                c.drawRightString(mx + main_w, my, dates)
            my -= body_size + 4
            # summary
            c.setFont(body_font, body_size)
            my = draw_wrapped(w.get('summary', ''), mx, my, main_w, body_font, body_size, leading=body_size + 3)
            my -= 4
            # highlights (bullets)
            for h in w.get('highlights', [])[:6]:
                my = draw_wrapped('• ' + h, mx + 6, my, main_w - 6, body_font, body_size, leading=body_size + 3)
                my -= 2
            my -= 6
            if my < margin_bottom + 50:
                c.showPage()
                my = height - margin_top

    # Education
    eds = resume.get('education', [])
    if eds:
        write_section('Education')
        for e in eds:
            left = f"{e.get('studyType','')} in {e.get('area','')}"
            right = f"{e.get('startDate','')} — {e.get('endDate','')}"
            c.setFont(header_font, body_size)
            c.drawString(mx, my, left)
            c.drawRightString(mx + main_w, my, right)
            my -= body_size + 4
            inst = e.get('institution', '')
            my = draw_wrapped(inst, mx, my, main_w, body_font, body_size, leading=body_size + 3)
            my -= 6

    # Projects expanded
    if projects:
        write_section('Projects')
        for p in projects[:8]:
            title = p.get('name', '')
            c.setFont(header_font, body_size)
            c.drawString(mx, my, title)
            my -= body_size + 4
            my = draw_wrapped(p.get('summary', ''), mx, my, main_w, body_font, body_size, leading=body_size + 3)
            my -= 6

    c.save()


if __name__ == '__main__':
    # Prefer using cv_renderer/generate_bankcv_pdf.py for path discovery and output handling.
    print('Tip: Run "python cv_renderer/generate_bankcv_pdf.py" to render from data/{timestamp}_{identifier}/resume.json')
