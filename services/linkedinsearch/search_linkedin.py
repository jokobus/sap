#!/usr/bin/env python3
"""Search for LinkedIn people profiles via SerpAPI (preferred) or DuckDuckGo fallback.

Saves results to a JSON file with entries containing: rank, name (if available), url, snippet, engine
"""

# run with
# python cv_generator/cv_generate_pdf.py

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import datetime
import urllib.parse
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

SERPAPI_KEY_ENV = "SERPAPI_API_KEY"


def build_query(keywords: List[str], company: Optional[str] = None, location: Optional[str] = None) -> str:
    """Build a simple LinkedIn profile search query - SUPPORTS 3-5 KEYWORDS"""
    parts = ["site:linkedin.com/in"]
    
    # Add company (most important)
    if company:
        parts.append(f'"{company}"')
    
    # Add location if provided
    if location:
        parts.append(f'"{location}"')
    
    # Add 3-5 keywords for better targeting
    if keywords:
        for k in keywords[:5]:  # Up to 5 keywords
            if k and len(k.strip()) > 0:
                clean_keyword = k.strip()
                # Quote multi-word keywords
                if ' ' in clean_keyword:
                    parts.append(f'"{clean_keyword}"')
                else:
                    parts.append(clean_keyword)
    
    return " ".join(parts)


def serpapi_search(query: str, num: int = 10, api_key: Optional[str] = None) -> List[Dict]:
    """Use SerpAPI Google engine to get organic results.

    Requires `serpapi` package and SERPAPI_API_KEY set.
    """
    try:
        from serpapi import GoogleSearch
    except Exception as e:
        raise RuntimeError("serpapi package not installed or import failed") from e

    params = {
        "engine": "google",
        "q": query,
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "num": num,
        "start": 0,
        "api_key": api_key,
    }

    search = GoogleSearch(params)
    res = search.get_dict()
    results = []
    for i, item in enumerate(res.get("organic_results", [])[:num], start=1):
        link = item.get("link") or item.get("url")
        title = item.get("title") or item.get("position")
        snippet = item.get("snippet") or item.get("rich_snippet", {}).get("top", {}).get("detected_extensions", "")
        results.append({"rank": i, "name": title, "url": link, "snippet": snippet, "engine": "serpapi"})
    return results


def ddg_html_search(query: str, num: int = 10, dump_html: Optional[str] = None, debug: bool = False) -> List[Dict]:
    """Fallback: use DuckDuckGo HTML interface and parse results.

    Not as reliable as SerpAPI, but works without API key.
    """
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # basic retry loop with exponential backoff
    resp = None
    for attempt in range(1, 4):
        try:
            resp = requests.post(url, data={"q": query}, headers=headers, timeout=10)
            resp.raise_for_status()
            break
        except Exception as e:
            if attempt >= 3:
                raise
            time.sleep(0.5 * (2 ** (attempt - 1)))

    if resp is None:
        return []

    if dump_html:
        try:
            with open(dump_html, "w", encoding="utf-8") as fh:
                fh.write(resp.text)
        except Exception:
            pass

    links = parse_ddg_html(resp.text, num=num, debug=debug)

    # if parsing found nothing, save a debug dump (use timestamped name) so user can inspect
    if not links:
        try:
            ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            debug_path = os.path.join("linkedinsearch", f"debug_ddg_{ts}.html")
            with open(debug_path, "w", encoding="utf-8") as fh:
                fh.write(resp.text)
            print(f"[debug] No results parsed — saved HTML to {debug_path}")
            low = resp.text.lower()
            if "captcha" in low or "recaptcha" in low or "verify" in low:
                print("[debug] Page contains likely anti-bot or captcha content.")
        except Exception:
            pass

    return links


def parse_ddg_html(html: str, num: int = 10, debug: bool = False) -> List[Dict]:
    """Parse DuckDuckGo HTML search results and extract LinkedIn profile links.

    Extracts links, decodes common redirect parameters and returns list of result dicts.
    """
    soup = BeautifulSoup(html, "html.parser")
    # Prefer result anchors if present
    a_tags = soup.select("a.result__a") or soup.find_all("a", href=True)
    if debug:
        print(f"[debug] total <a> tags found: {len(a_tags)}")
        sample = [a.get("href") for a in a_tags[:50]]
        print("[debug] sample hrefs:")
        for s in sample:
            print("  ", s)

    seen = set()
    rank = 0
    out = []
    for a in a_tags:
        href = a.get("href")
        if not href:
            continue

        # canonicalize duckduckgo redirect links if any (uddg param contains encoded target URL)
        try:
            parsed = urllib.parse.urlparse(href)
            qs = urllib.parse.parse_qs(parsed.query)
            if "uddg" in qs:
                href = urllib.parse.unquote(qs.get("uddg")[0])
            elif parsed.path.startswith("/l/") and "uddg" in qs:
                href = urllib.parse.unquote(qs.get("uddg")[0])
        except Exception:
            # keep original href on failure
            pass

        # normalize: remove fragments and query params
        try:
            p2 = urllib.parse.urlparse(href)
            netloc = (p2.netloc or "").lower()
            path = p2.path or ""
            href_norm = urllib.parse.urlunparse((p2.scheme or "https", netloc, path.rstrip("/"), "", "", ""))
        except Exception:
            href_norm = href

        # Must be a linkedin domain
        if "linkedin.com" not in href_norm:
            continue

        # Exclude known non-profile paths
        lower_path = path.lower()
        excluded_prefixes = ["/company", "/jobs", "/school", "/groups", "/pulse", "/posts", "/feed"]
        if any(lower_path.startswith(p) for p in excluded_prefixes):
            continue

        # Accept common profile patterns (/in/ or /pub/) and some vanity patterns
        if not re.search(r"^/(in|pub)/", lower_path) and not re.search(r"^/[a-z0-9-]+$", lower_path, re.I):
            # Not a profile-like path
            continue

        if href_norm in seen:
            continue
        seen.add(href_norm)

        rank += 1
        title = a.get_text(strip=True)
        snippet = ""
        parent = a.find_parent()
        if parent:
            p = parent.find_next_sibling("a") or parent.find_next_sibling("div")
            if p:
                snippet = p.get_text(strip=True)[:300]

        out.append({"rank": rank, "name": title, "url": href_norm, "snippet": snippet, "engine": "duckduckgo"})
        if rank >= num:
            break

    return out


def save_results(results: List[Dict], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def save_csv(results: List[Dict], path: str) -> None:
    import csv

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "name", "url", "snippet", "engine"])
        for r in results:
            writer.writerow([r.get("rank"), r.get("name"), r.get("url"), r.get("snippet"), r.get("engine")])


def dedupe_results(results: List[Dict]) -> List[Dict]:
    seen = set()
    out = []
    for r in results:
        u = r.get("url") or ""
        # normalize: remove query params and trailing slashes
        u_norm = re.sub(r"\?.*$", "", u).rstrip("/")
        if u_norm in seen:
            continue
        seen.add(u_norm)
        out.append(r)
    return out


def parse_args(argv: Optional[List[str]] = None):
    p = argparse.ArgumentParser(description="Search LinkedIn profiles using search engines and save top results to JSON.")
    p.add_argument("--keywords", "-k", nargs="+", required=True, help="Keywords or phrase(s) to search for. If a phrase has spaces, wrap it in quotes.")
    p.add_argument("--company", "-c", help="Optional company name to include in the query.")
    p.add_argument("--num", "-n", type=int, default=10, help="Number of profiles to fetch (default 10).")
    p.add_argument("--output", "-o", default="linkedinsearch/results.json", help="Output JSON file path.")
    p.add_argument("--use-serpapi", action="store_true", help="Force using SerpAPI (requires SERPAPI_API_KEY). By default will use SerpAPI if key is present.)")
    p.add_argument("--csv", help="Optional CSV output path (will be created alongside JSON if provided).")
    p.add_argument("--dedupe", action="store_true", help="Remove duplicate profile URLs (basic normalization).")
    p.add_argument("--debug", action="store_true", help="Print debug info such as sample hrefs from DuckDuckGo HTML.")
    p.add_argument("--dump-html", help="If provided, save DuckDuckGo HTML to this file for inspection.")
    p.add_argument("--post-filter", action="store_true", help="Require that keywords appear in title/snippet (may reduce results but increase relevance).")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None):
    args = parse_args(argv)
    query = build_query(args.keywords, args.company)
    print(f"Built query: {query}")

    results = []
    serp_key = os.environ.get(SERPAPI_KEY_ENV)
    # prefer serpapi if key provided or forced
    if args.use_serpapi or serp_key:
        key = serp_key
        if not key:
            print("SERPAPI_API_KEY not set; cannot use SerpAPI. Falling back to DuckDuckGo.")
        else:
            try:
                print("Using SerpAPI to query Google for best relevance...")
                results = serpapi_search(query, num=args.num, api_key=key)
            except Exception as e:
                print(f"SerpAPI search failed: {e}. Falling back to DuckDuckGo.")

    if not results:
        print("Using DuckDuckGo fallback (no API key). Results may be less consistent.")
        results = ddg_html_search(query, num=args.num, dump_html=args.dump_html, debug=args.debug)

    # Simple post-filter: ensure urls are linkedin person profiles
    filtered = []
    for r in results:
        u = r.get("url") or ""
        if re.search(r"linkedin\.com/(in|pub)/", u, re.I):
            filtered.append(r)

    # optional post-filter: require keywords appear in title or snippet
    if args.post_filter and filtered:
        kw_lower = [k.lower() for k in args.keywords]
        kept = []
        for r in filtered:
            text = ((r.get("name") or "") + " " + (r.get("snippet") or "")).lower()
            if any(k in text for k in kw_lower):
                kept.append(r)
        filtered = kept

    if args.dedupe:
        filtered = dedupe_results(filtered)

    # save CSV if requested
    if args.csv:
        try:
            save_csv(filtered, args.csv)
            print(f"Saved CSV to {args.csv}")
        except Exception as e:
            print(f"Failed to save CSV: {e}")

    save_results(filtered, args.output)
    print(f"Saved {len(filtered)} results to {args.output}")


if __name__ == "__main__":
    main()
