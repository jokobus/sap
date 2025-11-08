# LinkedIn scraper (demo)

This repository contains a small demo `linkedinscraper.py` that supports two modes:

- Mock/demo mode (default) — fast, safe, returns synthetic sample profiles (useful for demos/tests).
- Live mode (experimental) — attempts to log in to LinkedIn and scrape people search results using Selenium.

IMPORTANT: Scraping LinkedIn may violate their Terms of Service and/or applicable laws. Prefer the official LinkedIn API. Use the live mode only for legitimate purposes and with an account you control.

Requirements
------------
Install Python packages:

```powershell
python -m pip install -r requirements.txt
```

Usage
-----

Mock/demo:

```powershell
python linkedinscraper.py --company BMW --mock
```

Live (Selenium):

1. Set environment variables with your LinkedIn credentials (recommended):

```powershell
$env:LINKEDIN_EMAIL = 'hatev15120@fandoe.com'
$env:LINKEDIN_PASSWORD = '1568344-8t'
```

# LinkedIn scraper (demo)

This repository contains a demo `linkedinscraper.py` that supports a safe mock mode and an experimental live mode that uses Selenium to automate LinkedIn people searches.

IMPORTANT: Scraping LinkedIn may violate LinkedIn's Terms of Service and could trigger security or legal issues. Prefer the official LinkedIn API for production use. Use the live mode only with accounts you control and for legitimate purposes.

Requirements
------------
Install Python packages:

```powershell
python -m pip install -r requirements.txt
```

Quick examples
--------------

Mock/demo (returns canned BMW sample):

```powershell
python linkedinscraper.py --company BMW --mock
```

Live (Selenium) interactive run (recommended for debugging/captcha solve):

```powershell
$env:LINKEDIN_EMAIL = 'you@example.com'
$env:LINKEDIN_PASSWORD = 'your-password'
python linkedinscraper.py --company BMW --live --no-headless --debug
```

Live headless run (may be blocked by LinkedIn protections):

```powershell
python linkedinscraper.py --company BMW --live --debug
```

CLI flags (summary)
-------------------

- `--company, -c` (required): Company name to search (e.g. BMW).
- `--mock`: Use safe mock/demo data instead of live scraping.
- `--live`: Attempt live scraping with Selenium.
- `--debug`: Enable debug mode — saves screenshots and HTML on failures and prints verbose messages.
- `--email`: LinkedIn email (overrides `LINKEDIN_EMAIL` env var). Prefer env vars to avoid exposing secrets on the command line.
- `--password`: LinkedIn password (overrides `LINKEDIN_PASSWORD` env var).
- `--no-headless`: Run the browser in visible/headful mode (useful for manual captcha/2FA solve).
- `--cookie-file`: (reserved) Path to a cookie file to reuse an authenticated session (forwarded but not fully implemented).
- `--workers`: Number of parallel browser instances to run (default `1`). Each worker opens a full Chrome instance — choose small values.
- `--max`: Maximum number of results to return per worker (default `10`).
- `--keywords`: Extra keywords to include in the people search (e.g. "autonomous driving").
- `--title`: Job title to include in the search (e.g. "Senior Engineer").
- `--location`: Location to include in the search (e.g. "Munich").

Search behavior
---------------

The script builds a combined keywords query from `--company`, `--title`, `--keywords`, and `--location` and uses it for the LinkedIn people search (both the HTTP and Selenium flows).

Debugging and common failures
----------------------------

- LinkedIn uses anti-bot checks (reCAPTCHA, iframes, behavioral checks). If you see zero results, enable `--debug` and `--no-headless` and inspect the saved files like `debug_login.html` or `debug_no_results.html` and screenshots (e.g., `debug_no_results.png`). They reveal whether LinkedIn returned a login/captcha/blocked page or simply a different DOM structure.
- If a captcha or verification appears, run with `--no-headless` and complete it manually. For repeated runs, cookie reuse is the recommended flow — I can add `--save-cookies` / `--load-cookies` to help with that.

Security & legal notes
----------------------

- Do not scrape data you are not authorized to collect. Review LinkedIn's Terms of Service and relevant laws.
- For production or high-volume use, request API access from LinkedIn instead of scraping.

Next improvements available
-------------------------

- Cookie save/load (`--save-cookies` / `--load-cookies`) to reuse an authenticated session.
- Save results to file (`--save-json <path>`).
- Small anti-detection improvements (randomized delays, user-agent override). These are not guaranteed to bypass protections and may carry additional risk.

Contributing / push to repo
---------------------------

If you'd like me to commit and push these changes to the repository, I can attempt to create a git commit and push to the configured remote. You may be prompted for credentials if your remote requires authentication. If push fails, I'll show the error and give exact commands you can run locally.
