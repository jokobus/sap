#!/usr/bin/env python3
"""Generate a BankCV-styled PDF from a resume JSON using cv_renderer.

Expected layout:
  data/{timestamp}_{identifier}/resume.json  -> writes resume.pdf in same folder

Usage:
    python cv_generator/cv_generate_pdf.py               # auto-picks latest data folder
    python cv_generator/cv_generate_pdf.py --dir PATH    # explicit data subfolder
    python cv_generator/cv_generate_pdf.py --file FILE   # explicit resume.json file
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from cv_generator.cv_renderer import resume_to_pdf_bankcv


def find_latest_data_dir(data_root: Path) -> Optional[Path]:
    if not data_root.exists():
        return None
    candidates = []
    for child in data_root.iterdir():
        if child.is_dir():
            resume_file = child / 'resume.json'
            if resume_file.exists():
                # prefer mtime of resume.json; fallback to dir mtime
                try:
                    ts = resume_file.stat().st_mtime
                except Exception:
                    ts = child.stat().st_mtime
                candidates.append((ts, child))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Render resume.json to resume.pdf (BankCV style).')
    parser.add_argument('--dir', dest='dir', help='Path to data/{timestamp}_{identifier} folder containing resume.json')
    parser.add_argument('--file', dest='file', help='Explicit path to resume.json')
    args = parser.parse_args(argv)

    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent  # cv_generator/ -> repo root
    data_root = repo_root / 'data'

    resume_path: Optional[Path] = None
    out_dir: Optional[Path] = None

    if args.file:
        resume_path = Path(args.file)
        out_dir = resume_path.parent
    elif args.dir:
        out_dir = Path(args.dir)
        resume_path = out_dir / 'resume.json'
    else:
        # auto-pick latest in data/*/resume.json
        latest = find_latest_data_dir(data_root)
        if latest is not None:
            out_dir = latest
            resume_path = latest / 'resume.json'

    # Fallback to legacy candidates (repo root) if nothing found
    if resume_path is None or not resume_path.exists():
        legacy_candidates = [
            repo_root / 'tailored_resume_20251108_235714.json',
            repo_root / 'Shishir_Sunar.resume.json',
        ]
        for p in legacy_candidates:
            if p.exists():
                resume_path = p
                out_dir = p.parent
                break

    if resume_path is None or not resume_path.exists():
        print('Error: No resume.json found. Looked in:')
        print(' -', data_root / '{timestamp}_{identifier}/resume.json')
        print(' - legacy candidates in repo root')
        return 1

    # Load resume
    with open(resume_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Determine output path (resume.pdf in the same directory)
    out_dir = out_dir or resume_path.parent
    out_pdf = out_dir / 'resume.pdf'
    resume_to_pdf_bankcv(data, str(out_pdf))
    print('Saved', out_pdf)
    return 0


if __name__ == '__main__':
    sys.exit(main())
