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


def live_get_employee_profiles(company_name, max_results=10, headless=True, email=None, password=None, cookie_file=None, debug=False, keywords=None, title=None, location=None, keep_open=False):
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
    # Allow an interactive manual login flow when running headful with --keep-open
    interactive_login_allowed = keep_open and not headless
    if not (email and password) and not cookie_file and not interactive_login_allowed:
        raise RuntimeError('LinkedIn credentials required for live scraping. Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD env vars, provide a cookie file, or run with --no-headless --keep-open to sign in manually.')

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

    # Directory where this script lives (it's already inside linkedinscraper/)
    script_dir = os.path.dirname(__file__) or os.getcwd()
    os.makedirs(script_dir, exist_ok=True)

    def _save_debug_artifacts(name):
        """Save screenshot and HTML to the linkedinscraper folder with a timestamped name."""
        ts = int(time.time())
        png_path = os.path.join(script_dir, f"debug_{name}_{ts}.png")
        html_path = os.path.join(script_dir, f"debug_{name}_{ts}.html")
        try:
            driver.save_screenshot(png_path)
        except Exception:
            pass
        try:
            open(html_path, 'w', encoding='utf-8').write(driver.page_source)
        except Exception:
            pass
        if debug:
            print(f"[debug] Saved {png_path} and {html_path}")

    def _detect_protection():
        """Detect common LinkedIn anti-bot feedback in the current page source.

        Returns a tuple (detected: bool, reason: str)
        """
        try:
            src = (driver.page_source or '').lower()
        except Exception:
            return (False, '')

        phrases = [
            "you don't have access to this profile",
            'grow your network first',
            'recaptcha',
            'g-recaptcha',
            'are you a robot',
            'access to this profile',
            'complete the captcha',
        ]
        for p in phrases:
            if p in src:
                return (True, p)
        return (False, '')

    def save_cookies_to_file(driver, path):
        try:
            cookies = driver.get_cookies()
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f)
            if debug:
                print(f"[debug] Saved {len(cookies)} cookies to {path}")
        except Exception as e:
            if debug:
                print(f"[debug] Failed to save cookies: {e}")

    def load_cookies_from_file(driver, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
        except Exception as e:
            if debug:
                print(f"[debug] Failed to read cookies from {path}: {e}")
            return False

        # Navigate to base domain so cookies can be set
        driver.get('https://www.linkedin.com/')
        added = 0
        for c in cookies:
            cookie = {k: v for k, v in c.items() if k in ('name', 'value', 'path', 'domain', 'expiry', 'secure', 'httpOnly')}
            try:
                driver.add_cookie(cookie)
                added += 1
            except Exception:
                # try without domain
                cookie2 = cookie.copy()
                cookie2.pop('domain', None)
                try:
                    driver.add_cookie(cookie2)
                    added += 1
                except Exception:
                    if debug:
                        print(f"[debug] Could not add cookie {cookie.get('name')}")
        if debug:
            print(f"[debug] Added {added} cookies from {path}")
        driver.refresh()
        return True

    try:
        wait = WebDriverWait(driver, 15)
        # Try loading cookies (if provided) before logging in
        if cookie_file:
            if os.path.exists(cookie_file):
                if debug:
                    print(f"[debug] Loading cookies from {cookie_file}")
                load_cookies_from_file(driver, cookie_file)
            else:
                if debug:
                    print(f"[debug] Cookie file {cookie_file} not found, continuing to login flow")

        # If cookies were loaded, check if we're already logged in
        logged_in = False
        try:
            # short wait
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="Search"]')))
            logged_in = True
            if debug:
                print('[debug] Session restored from cookies, logged in')
        except Exception:
            logged_in = False

        # If not logged in, perform credential login
        if not logged_in:
            if debug:
                print('[debug] Opening LinkedIn login page')
            # If credentials are available, use them; otherwise allow manual interactive login
            driver.get('https://www.linkedin.com/login')
            if email and password:
                try:
                    wait.until(EC.presence_of_element_located((By.ID, 'username')))
                except Exception as e:
                    if debug:
                        print(f'[debug] username field not found: {e}')
                        try:
                            _save_debug_artifacts('after_login_page')
                        except Exception:
                            pass
                    raise
                driver.find_element(By.ID, 'username').send_keys(email)
                driver.find_element(By.ID, 'password').send_keys(password)
                driver.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()

                # Wait for homepage to load (profile nav or search box)
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="Search"]')))
                    logged_in = True
                except Exception as e:
                    if debug:
                        print(f'[debug] Search input not found after login: {e}')
                        try:
                            _save_debug_artifacts('login')
                        except Exception:
                            pass
                    raise
            else:
                # No credentials provided; if interactive login is allowed, pause and let the user sign in manually
                if debug:
                    print('[debug] No credentials provided; entering manual interactive login mode')
                try:
                    print('[info] Please sign in interactively in the opened browser window. When finished, return here and press Enter to continue...')
                    input('Press Enter after you have completed the interactive login in the browser...')
                    # After the user signals, try to detect login by waiting for the search input
                    try:
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="Search"]')), timeout=30)
                        logged_in = True
                    except Exception:
                        # don't raise here; we'll continue and detection may occur later
                        logged_in = False
                except Exception:
                    logged_in = False

        # If logged in and save path provided via cookie_file, persist cookies
        if logged_in and cookie_file:
            try:
                save_cookies_to_file(driver, cookie_file)
            except Exception:
                if debug:
                    print(f'[debug] Failed to save cookies to {cookie_file}')

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

        # Detect common protection pages (e.g., access-message or captcha)
        try:
            prot, reason = _detect_protection()
            if prot:
                message = ('LinkedIn protection detected ("' + reason + '"). ' \
                           'This usually means LinkedIn blocked automated access: try running with --no-headless --keep-open, solve any captcha/2FA manually, then use --save-cookies to persist the session.')
                print(f'[warning] {message}')
                if debug:
                    try:
                        _save_debug_artifacts('protection')
                    except Exception:
                        pass
                # If user requested keep_open and we have a visible browser, pause so they can act
                if keep_open and not headless:
                    try:
                        input('Press Enter after you have resolved the protection (close any popups) to continue...')
                    except Exception:
                        pass
                # Stop further automated scraping for this session
                return []
        except Exception:
            pass

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
                                _save_debug_artifacts('search')
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

        # Re-check for protection after page load/scroll (captchas sometimes appear after navigation)
        try:
            prot, reason = _detect_protection()
            if prot:
                print(f'[warning] LinkedIn protection detected after page load ("{reason}").')
                if debug:
                    try:
                        _save_debug_artifacts('protection_after_scroll')
                    except Exception:
                        pass
                if keep_open and not headless:
                    try:
                        input('Press Enter after you have resolved the protection (close any popups) to continue...')
                    except Exception:
                        pass
                return []
        except Exception:
            pass

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
                _save_debug_artifacts('no_results')
            except Exception:
                pass

        if debug:
            print(f'[debug] Returning {len(results)} results')

        return results
    finally:
        # If keep_open is True, wait for user input before quitting so manual interaction is possible.
        try:
            if keep_open and not headless:
                print('[info] --keep-open set: browser will remain open until you press Enter')
                input('Press Enter to close the browser and continue...')
        except Exception:
            pass

        driver.quit()


def get_employee_profiles_live(company_name, max_results=10, headless=True, debug=False, email=None, password=None, cookie_file=None, keywords=None, title=None, location=None, keep_open=False):
    try:
        return live_get_employee_profiles(company_name, max_results=max_results, headless=headless, debug=debug, email=email, password=password, cookie_file=cookie_file, keywords=keywords, title=title, location=location, keep_open=keep_open)
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
    parser.add_argument('--cookie-file', type=str, help='Optional path to a cookie file to load and save session cookies')
    parser.add_argument('--save-cookies', type=str, help='Path to save cookies after login (optional)')
    parser.add_argument('--keywords', type=str, help='Additional keywords to include in the LinkedIn people search (e.g. "data scientist")')
    parser.add_argument('--title', type=str, help='Job title to filter by (e.g. "Senior Engineer")')
    parser.add_argument('--location', type=str, help='Location to filter by (e.g. "Munich")')
    parser.add_argument('--load-cookies', type=str, help='Path to a cookie file to load before login')
    parser.add_argument('--workers', type=int, default=1, help='Number of parallel browser instances to run (default 1)')
    parser.add_argument('--max', type=int, default=10, help='Maximum sample results to return')
    parser.add_argument('--keep-open', '--pause-after-login', action='store_true', help='Keep the browser open after login until you press Enter (useful for manual captcha/2FA solve)')
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
                        cookie_file=args.cookie_file or args.load_cookies,
                        keywords=args.keywords,
                        title=args.title,
                        location=args.location,
                        keep_open=args.keep_open,
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
                cookie_file=args.load_cookies or args.cookie_file,
                keywords=args.keywords,
                title=args.title,
                location=args.location,
                keep_open=args.keep_open,
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
