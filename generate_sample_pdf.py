#!/usr/bin/env python3
"""Generate a sample PDF using resume_tailor.resume_to_pdf.

Usage: python generate_sample_pdf.py
"""
import json
import os
from pathlib import Path

from resume_tailor import resume_to_pdf

candidates = [
    'tailored_resume_20251108_235714.json',
    'tailored_resume_20251108_235714.JSON',
    'Shishir_Sunar.resume.json',
]

found = None
for name in candidates:
    if Path(name).exists():
        found = name
        break

if not found:
    print('No input JSON found in workspace. Place a resume JSON next to this script named one of:', candidates)
    raise SystemExit(1)

with open(found, 'r', encoding='utf-8') as f:
    data = json.load(f)

out = f'sample_resume_preview.pdf'
resume_to_pdf(data, out)
print('Saved', out)
