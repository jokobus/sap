import os
import requests
from bs4 import BeautifulSoup
import time
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.common.keys import Keys
except Exception:
    # Will raise a clear error when attempting live mode if selenium isn't installed
    webdriver = None
    TimeoutException = None
    Keys = None


def get_employee_profiles(company_name, use_mock=True, max_results=10, keywords=None, title=None, location=None):
    """
    Get employee profile data for a company.

    - If use_mock is True, returns a small static sample appropriate for demos/tests.
    - If use_mock is False, attempts a live request to LinkedIn (may fail due to bot protections).

    Returns list of dicts with keys: name, profile_link [, title]
    """
    if use_mock:
        # Provide a small realistic-looking sample for BMW
        sample_bmw = [
            {
                'name': 'Dr. Markus Weber',
                'profile_link': 'https://www.linkedin.com/in/markus-weber-bmw',
                'title': 'Senior Engineer at BMW AG'
            },
            {
                'name': 'Anna Müller',
                'profile_link': 'https://www.linkedin.com/in/anna-mueller-bmw',
                'title': 'Product Manager, BMW ConnectedDrive'
            },
            {
                'name': 'James Smith',
                'profile_link': 'https://www.linkedin.com/in/james-smith-bmw',
                'title': 'UX Designer at BMW Group'
            }
        ]

        # If user asked for BMW, return the curated sample, otherwise return generic sample names
        if company_name and company_name.strip().lower() in ('bmw', 'bwm', 'bayerische motoren werke'):
            return sample_bmw[:max_results]
        else:
            generic = [
                {'name': f'Employee {i+1}', 'profile_link': f'https://www.linkedin.com/in/employee-{i+1}', 'title': 'Role'}
                for i in range(max_results)
            ]
            return generic

    # --- Live scraping branch (best-effort) ---
    # Note: LinkedIn actively defends against scraping. Use the official API where possible.
    # Build a keywords query from available fields. For simple public HTTP scraping we use a keywords param
    parts = []
    if company_name:
        parts.append(company_name)
    if title:
        parts.append(title)
    if keywords:
        parts.append(keywords)
    if location:
        parts.append(location)
    combined = ' '.join(parts).strip()
    if not combined:
        combined = company_name or ''
    search_url = f"https://www.linkedin.com/search/results/people/?keywords={requests.utils.requote_uri(combined)}"
    headers = {
        # Use a realistic User-Agent. The user should replace this with their own if doing live requests.
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
    except Exception as e:
        print(f"Request failed: {e}")
        return None

    if response.status_code != 200:
        print(f"Failed to retrieve profiles: HTTP {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    # NOTE: LinkedIn's HTML changes often; this selector is likely not correct for live scraping.
    profiles = soup.find_all('a', class_='search-result__result-link')

    employee_data = []
    for profile in profiles[:max_results]:
        # Defensive parsing: ensure tags exist before accessing
        name_tag = profile.find('span', class_='name')
        name = name_tag.text.strip() if name_tag else profile.get_text(strip=True)
        profile_link = profile.get('href') or ''
        employee_data.append({'name': name, 'profile_link': profile_link})

    return employee_data


def live_get_employee_profiles(company_name, max_results=10, headless=True, email=None, password=None, cookie_file=None, debug=False, keywords=None, title=None, location=None):
    """
    Attempt live scraping using Selenium.

    - Requires `selenium` and `webdriver-manager` installed.
    - Prefer providing credentials via LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables.
    - Optionally accepts a cookie file (not implemented here, reserved for future use).

    Returns list of dicts with keys: name, profile_link, title (when found)
    """
    if webdriver is None:
        raise RuntimeError('Selenium or webdriver-manager not installed. Install via requirements.txt')

    # Credentials
    email = email or os.environ.get('LINKEDIN_EMAIL')
    password = password or os.environ.get('LINKEDIN_PASSWORD')
    if not email or not password:
        raise RuntimeError('LinkedIn credentials required for live scraping. Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD env vars.')

    options = webdriver.ChromeOptions()
    if headless:
        # Use new headless mode where supported
        options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        wait = WebDriverWait(driver, 15)
        # Login
        if debug:
            print('[debug] Opening LinkedIn login page')
        driver.get('https://www.linkedin.com/login')
        try:
            wait.until(EC.presence_of_element_located((By.ID, 'username')))
        except Exception as e:
            if debug:
                print(f'[debug] username field not found: {e}')
                try:
                    open('debug_after_login_page.html','w',encoding='utf-8').write(driver.page_source)
                except Exception:
                    pass
            raise
        driver.find_element(By.ID, 'username').send_keys(email)
        driver.find_element(By.ID, 'password').send_keys(password)
        driver.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()

        # Wait for homepage to load (profile nav or search box)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="Search"]')))
        except Exception as e:
            if debug:
                print(f'[debug] Search input not found after login: {e}')
                try:
                    driver.save_screenshot('debug_login.png')
                    open('debug_login.html','w',encoding='utf-8').write(driver.page_source)
                    print('[debug] Saved debug_login.png and debug_login.html')
                except Exception as _:
                    pass
            raise

        # Build a people search URL. Using keywords/title/location to find people related to the company.
        parts = []
        if company_name:
            parts.append(company_name)
        if title:
            parts.append(title)
        if keywords:
            parts.append(keywords)
        if location:
            parts.append(location)
        search_query = ' '.join(parts).strip() or company_name
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={requests.utils.requote_uri(search_query)}"
        driver.get(search_url)

        # Wait for results (try a few strategies)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.search-results-container, ul.reusable-search__entity-results-list, div.reusable-search__entity-result-list')))
        except Exception:
            # Try triggering the search via the top search box as a fallback
            if debug:
                print('[debug] No results container found by selector, attempting manual search via search box')
            try:
                search_box = driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="Search"]')
                search_box.clear()
                search_box.send_keys(company_name)
                if Keys:
                    search_box.send_keys(Keys.ENTER)
                time.sleep(2)
            except Exception as e:
                if debug:
                    print(f'[debug] manual search failed: {e}')
                    try:
                        driver.save_screenshot('debug_search.png')
                        open('debug_search.html','w',encoding='utf-8').write(driver.page_source)
                        print('[debug] Saved debug_search.png and debug_search.html')
                    except Exception:
                        pass
                # continue; containers finding below will handle empty case

        # Scroll a few times to load results
        last_height = driver.execute_script('return document.body.scrollHeight')
        for _ in range(3):
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(1.5)
            new_height = driver.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height

        # Collect result containers (try multiple selectors for robustness)
        containers = driver.find_elements(By.CSS_SELECTOR, 'li.reusable-search__result-container, div.search-result__info, div.entity-result__item, div.entity-result')

        if debug:
            print(f'[debug] Found {len(containers)} raw container elements')

        results = []
        for c in containers:
            if len(results) >= max_results:
                break
            try:
                # Name
                name = None
                try:
                    name_el = c.find_element(By.CSS_SELECTOR, 'span.entity-result__title-text a span, span[dir="ltr"]')
                    name = name_el.text.strip()
                except Exception:
                    try:
                        name = c.find_element(By.TAG_NAME, 'a').text.strip()
                    except Exception:
                        name = ''

                # Profile link (first anchor with /in/)
                profile_link = ''
                try:
                    anchors = c.find_elements(By.TAG_NAME, 'a')
                    for a in anchors:
                        href = a.get_attribute('href') or ''
                        if '/in/' in href:
                            profile_link = href
                            break
                    if not profile_link and anchors:
                        profile_link = anchors[0].get_attribute('href') or ''
                except Exception:
                    profile_link = ''

                # Title or subtitle
                title = ''
                try:
                    title_el = c.find_element(By.CSS_SELECTOR, 'div.entity-result__primary-subtitle, div.search-result__snippets')
                    title = title_el.text.strip()
                except Exception:
                    title = ''

                results.append({'name': name, 'profile_link': profile_link, 'title': title})
            except Exception:
                continue

        if debug and len(results) == 0:
            try:
                driver.save_screenshot('debug_no_results.png')
                open('debug_no_results.html','w',encoding='utf-8').write(driver.page_source)
                print('[debug] No results: saved debug_no_results.png and debug_no_results.html')
            except Exception:
                pass

        if debug:
            print(f'[debug] Returning {len(results)} results')

        return results
    finally:
        driver.quit()


def get_employee_profiles_live(company_name, max_results=10, headless=True, debug=False, email=None, password=None, cookie_file=None, keywords=None, title=None, location=None):
    try:
        return live_get_employee_profiles(company_name, max_results=max_results, headless=headless, debug=debug, email=email, password=password, cookie_file=cookie_file, keywords=keywords, title=title, location=location)
    except Exception as e:
        print(f'Live scraping failed: {e}')
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description='LinkedIn scraper demo (mock by default).')
    parser.add_argument('--company', '-c', required=True, help='Company name to search (e.g. BMW)')
    parser.add_argument('--mock', action='store_true', help='Use mock/sample output instead of live scraping')
    parser.add_argument('--live', action='store_true', help='Attempt live scraping using Selenium (requires credentials and dependencies)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode: save screenshots/html and verbose prints')
    parser.add_argument('--email', type=str, help='LinkedIn email (overrides LINKEDIN_EMAIL env var)')
    parser.add_argument('--password', type=str, help='LinkedIn password (overrides LINKEDIN_PASSWORD env var)')
    parser.add_argument('--no-headless', action='store_true', help='Run browser in visible mode (not headless)')
    parser.add_argument('--cookie-file', type=str, help='Optional path to a cookie file to reuse an authenticated session')
    parser.add_argument('--keywords', type=str, help='Additional keywords to include in the LinkedIn people search (e.g. "data scientist")')
    parser.add_argument('--title', type=str, help='Job title to filter by (e.g. "Senior Engineer")')
    parser.add_argument('--location', type=str, help='Location to filter by (e.g. "Munich")')
    parser.add_argument('--workers', type=int, default=1, help='Number of parallel browser instances to run (default 1)')
    parser.add_argument('--max', type=int, default=10, help='Maximum sample results to return')
    args = parser.parse_args(argv)

    if args.live:
        headless = not bool(args.no_headless)
        # If workers > 1, run multiple browser instances in parallel
        if args.workers and args.workers > 1:
            workers = max(1, args.workers)
            futures = []
            combined_results = []
            with ThreadPoolExecutor(max_workers=workers) as ex:
                for i in range(workers):
                    futures.append(ex.submit(
                        get_employee_profiles_live,
                        args.company,
                        max_results=args.max,
                        headless=headless,
                        debug=args.debug,
                        email=args.email,
                        password=args.password,
                        cookie_file=args.cookie_file,
                        keywords=args.keywords,
                        title=args.title,
                        location=args.location,
                    ))
                    # small stagger to avoid simultaneous spikes
                    time.sleep(0.5)

                for fut in as_completed(futures):
                    try:
                        r = fut.result()
                        if r:
                            combined_results.extend(r)
                    except Exception as e:
                        print(f'Worker failed: {e}')

            results = combined_results
        else:
            results = get_employee_profiles_live(
                args.company,
                max_results=args.max,
                headless=headless,
                debug=args.debug,
                email=args.email,
                password=args.password,
                cookie_file=args.cookie_file,
                keywords=args.keywords,
                title=args.title,
                location=args.location,
            )
    else:
        results = get_employee_profiles(args.company, use_mock=args.mock, max_results=args.max, keywords=args.keywords, title=args.title, location=args.location)

    if results is None:
        print('No results (live scraping may have failed or returned nothing).')
        sys.exit(1)

    # Print JSON so it's easy to consume
    print(json.dumps({'company': args.company, 'results': results}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
