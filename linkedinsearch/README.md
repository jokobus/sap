# linkedinsearch

Small helper to search for LinkedIn people profiles via web search engines and save the most relevant results to a JSON file.

Key points:
- This tool builds focused search queries using site:linkedin.com filters and exclusions so results are people profiles (not posts or company pages).
- It uses SerpAPI (if you set `SERPAPI_API_KEY`) for reliable, high-quality Google results. If no key is provided it falls back to scraping DuckDuckGo HTML search results.

Files
- `search_linkedin.py` — main CLI script.
- `requirements.txt` — Python deps.

Quick start (PowerShell):

```powershell
python .\linkedinsearch\search_linkedin.py --keywords "data scientist" --company BMW --output linkedinsearch/results.json --num 20
```

Environment
- To use SerpAPI (recommended for best relevance), set environment variable `SERPAPI_API_KEY` to your SerpAPI key.

Query tips for best relevance
- Include exact role/title in quotes: "Data Scientist"
- Add company name (if searching for people at a company) with `--company`.
- Add location words (e.g., "Berlin") to prefer local profiles.
- Use multiple keywords to narrow results (space-separated).
- The script builds queries like:
  site:linkedin.com/in OR site:linkedin.com/pub "Data Scientist" "BMW" -site:linkedin.com/company -inurl:/posts/ -inurl:/feed/ -inurl:/jobs/

Notes
- This script does not log into LinkedIn and only collects public profile URLs returned by search engines.
- For production or heavy usage, use SerpAPI or a paid search API to avoid blocking and increase reliability.

Debugging & tests
------------------

This project contains improved DuckDuckGo HTML parsing and basic debug helpers to make diagnosing empty/blocked results easier.

- The DuckDuckGo fetch now uses realistic request headers, a timeout, and a small retry loop to reduce transient failures.
- The HTML parser was refactored into `parse_ddg_html()` which decodes common DuckDuckGo redirect parameters (like `uddg=`), normalizes URLs, and filters out non-profile LinkedIn paths (company, jobs, posts, etc.).
- If the parser finds no LinkedIn results, the script will automatically save the returned HTML to `linkedinsearch/debug_ddg_<timestamp>.html` so you can inspect whether the search engine returned a consent/captcha/blocked page or a changed DOM.

Test fixture and a lightweight test runner are included to validate the parser without additional test dependencies:

Run the quick test locally:

```powershell
python tests/run_tests.py
```

This reads `linkedinsearch/fixtures/ddg_sample.html` and checks that the parser extracts expected LinkedIn profile URLs. Use this as a starting point for adding more fixtures (different result DOMs) to guard against future parsing regressions.

Dependencies
------------

Make sure the environment has the required packages installed for running the script and the parser tests:

```powershell
python -m pip install -r linkedinsearch/requirements.txt
```

If you prefer `pytest`, you can convert `tests/run_tests.py` to a pytest-based test file and run `pytest` in CI.
