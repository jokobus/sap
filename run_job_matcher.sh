#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ ! -d venv ]; then
  python3 -m venv venv
fi

./venv/bin/pip install -q google-generativeai

if [ -z "${GOOGLE_API_KEY:-}" ]; then
  echo "Please set GOOGLE_API_KEY environment variable."
  echo "export GOOGLE_API_KEY=\"your-key\""
  exit 1
fi

./venv/bin/python job_matcher.py
