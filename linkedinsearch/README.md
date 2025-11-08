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
