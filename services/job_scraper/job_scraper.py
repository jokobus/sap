import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed 
from flair.models import SequenceTagger
from flair.data import Sentence

flair_model = SequenceTagger.load("kaliani/flair-ner-skill")

experience_level_mapping = {
    "Internship": "f_E=1",
    "Entry level": "f_E=2",
    "Associate": "f_E=3",
    "Mid-Senior level": "f_E=4",
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)",
]

# logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def create_session():
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers.update({"Accept-Language": "en-US,en;q=0.9"})
    return s

def rand_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

def fetch_fragment(session, keywords, location, start=0, experience=None):
    base = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {"keywords": keywords, "location": location, "start": start}
    if experience:
        params["f_E"] = experience_level_mapping.get(experience, experience)
    resp = session.get(base, headers=rand_headers(), params=params, timeout=15)
    resp.raise_for_status()
    return resp.text

def parse_job_cards(html_fragment):
    soup = BeautifulSoup(html_fragment, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/jobs/view/" in href:
            title = a.get_text(strip=True)
            links.append({"title": title, "url": href})
    # deduplicate by url
    seen = set()
    dedup = []
    for l in links:
        if l["url"] not in seen:
            seen.add(l["url"])
            dedup.append(l)
    return dedup

def fetch_job_page(session, url):
    try:
        r = session.get(url, headers=rand_headers(), timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        logging.debug(f"job page fetch failed {url}: {e}")
        return ""

def extract_job_info(html, url):
    soup = BeautifulSoup(html, "html.parser")
    title = None
    company = None
    location = None
    description = None
    # try structured JSON-LD
    j = soup.find("script", type="application/ld+json")
    if j:
        try:
            import json
            jd = json.loads(j.string)
            title = jd.get("title") or title
            company = jd.get("hiringOrganization", {}).get("name") or company
            location = jd.get("jobLocation", {}).get("address", {}).get("addressLocality") or location
            description = jd.get("description") or description
        except Exception:
            pass
    # fallbacks
    if not title:
        t = soup.find(lambda tag: tag.name in ["h1", "h2"] and "job" in (tag.get("class") or [""])[0].lower() if tag.get("class") else False)
        if t:
            title = t.get_text(strip=True)
    if not company:
        c = soup.find("a", {"data-tracking-control-name": "public_jobs_topcard-org-link"})
        if c:
            company = c.get_text(strip=True)
    if not description:
        desc_div = soup.find("div", {"class": lambda c: c and ("description" in c or "job-description" in c)})
        if desc_div:
            description = desc_div.get_text(separator=" ", strip=True)
    if not description:
        # try long text blocks
        ps = soup.find_all("section")
        for p in ps:
            txt = p.get_text(strip=True)
            if len(txt) > 200:
                description = txt
                break
    return {
        "title": title or "",
        "company": company or "",
        "location": location or "",
        "url": url,
        "description": description or "",
    }

def extract_skills_from_text(text):
    if not text or len(text.strip()) < 10:
        return []
    s = Sentence(text)
    flair_model.predict(s)
    skills = []
    for ent in s.get_spans("ner"):
        if ent.tag == "SKILL" or "skill" in ent.tag.lower():
            skills.append(ent.text)
    # heuristic dedupe and top-k
    uniq = list(dict.fromkeys([x.strip() for x in skills if x.strip()]))
    return uniq[:25]

def worker_fetch_and_parse(session, job_meta):
    url = job_meta["url"]
    html = fetch_job_page(session, url)
    info = extract_job_info(html, url)
    info["skills"] = extract_skills_from_text(info["description"])
    return info

def scrape_linkedin_jobs(keywords="software engineer", location="Worldwide", pages=3, results_per_page=25, experience=None, max_workers=6, out_csv="linkedin_jobs.csv"):
    session = create_session()
    results = []
    starts = [i * results_per_page for i in range(pages)]
    job_links = []
    for start in starts:
        frag = fetch_fragment(session, keywords, location, start=start, experience=experience)
        cards = parse_job_cards(frag)
        job_links.extend(cards)
        time.sleep(random.uniform(1.2, 2.5))
    # limit unique urls
    unique = []
    seen = set()
    for j in job_links:
        if j["url"] not in seen:
            seen.add(j["url"])
            unique.append(j)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(worker_fetch_and_parse, session, jm) for jm in unique]
        for f in as_completed(futures):
            try:
                info = f.result()
                results.append(info)
                logging.info(f"fetched: {info.get('title')[:60]} - {info.get('company')[:40]}")
                time.sleep(random.uniform(0.6, 1.8))
            except Exception as e:
                logging.debug(f"worker error: {e}")
    df = pd.DataFrame(results)
    df.to_csv(out_csv, index=False)
    return df

if __name__ == "__main__":
    df = scrape_linkedin_jobs(
        keywords="machine learning engineer",
        location="Germany",
        pages=4,
        results_per_page=25,
        experience="Entry level",
        max_workers=5,
        out_csv="ml_jobs_de.csv",
    )
    print(df.head())
