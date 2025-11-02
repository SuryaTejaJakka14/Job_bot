"""
Complete working scraper for jobs.nvoids.com
Reads the actual HTML table structure and extracts jobs.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import logging
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import (
    USER_AGENT,
    TARGET_KEYWORDS,
    EXCLUDE_KEYWORDS,
    MIN_YEARS_EXPERIENCE,
    HEADLESS_BROWSER,
    MAX_WORKERS
)

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

CHROME_SERVICE = None

def get_chrome_service():
    global CHROME_SERVICE
    if CHROME_SERVICE is None:
        CHROME_SERVICE = Service(ChromeDriverManager().install())
    return CHROME_SERVICE

def setup_driver():
    chrome_options = Options()
    if HEADLESS_BROWSER:
        chrome_options.add_argument('--headless=new')
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(f'user-agent={USER_AGENT}')
    
    service = get_chrome_service()
    return webdriver.Chrome(service=service, options=chrome_options)

def extract_email(text):
    if not text:
        return None
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    excluded = ['usjobs@nvoids.com', 'resumes@nvoids.com', 'nvoids.jobs@gmail.com']
    for email in matches:
        if email.lower() not in excluded:
            return email
    return None

def is_relevant_job(title):
    title_lower = title.lower()
    for exclude in EXCLUDE_KEYWORDS:
        if exclude.lower() in title_lower:
            return False
    if not TARGET_KEYWORDS:
        return True
    for keyword in TARGET_KEYWORDS:
        if keyword.lower() in title_lower:
            return True
    return False

def scrape_job_detail(job_url):
    """Scrape individual job detail page."""
    driver = None
    try:
        driver = setup_driver()
        driver.get(job_url)
        time.sleep(1)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table')
        
        if not table:
            return None
        
        first_row = table.find('tr')
        if not first_row:
            return None
        
        title_text = first_row.get_text(strip=True)
        if ' at ' in title_text:
            title = title_text.split(' at ')[0].strip()
            location = title_text.split(' at ')[1].strip()
        else:
            title = title_text
            location = "Not specified"
        
        if not is_relevant_job(title):
            return None
        
        page_text = soup.get_text()
        email = extract_email(page_text)
        
        if not email:
            return None
        
        company = email.split('@')[1].split('.')[0].capitalize() if '@' in email else "Unknown"
        job_id = job_url.split('jid=')[1].split('&')[0] if 'jid=' in job_url else job_url
        
        return {
            'job_id': job_id,
            'title': title,
            'company': company,
            'email': email,
            'url': job_url,
            'location': location
        }
    
    except Exception as e:
        logging.error(f"Error scraping {job_url}: {str(e)}")
        return None
    finally:
        if driver:
            driver.quit()

def scrape_jobs_parallel(unused_url=None, max_workers=None):
    """Scrape all jobs from the search page."""
    if max_workers is None:
        max_workers = MAX_WORKERS
    
    all_jobs = []
    driver = None
    
    try:
        print(f"\n{'='*70}")
        print(f"JOB SCRAPER - READING TABLE FROM SEARCH PAGE")
        print(f"{'='*70}\n")
        
        driver = setup_driver()
        driver.get("https://jobs.nvoids.com/search_sph.jsp")
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find the main table with jobs
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables on page")
        
        if len(tables) < 2:
            print("✗ Expected table not found")
            return all_jobs
        
        # The main job table is usually the second table
        job_table = tables[1] if len(tables) > 1 else tables[0]
        rows = job_table.find_all('tr')
        
        print(f"Found {len(rows)} rows in job table")
        
        job_urls = []
        
        # Process each row (skip header)
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
            
            # Find all links in this row
            links = row.find_all('a', href=re.compile(r'job_details'))
            
            for link in links:
                href = link.get('href')
                if href:
                    # Build full URL
                    if href.startswith('job_details'):
                        full_url = f"https://jobs.nvoids.com/{href}"
                    elif href.startswith('/'):
                        full_url = f"https://jobs.nvoids.com{href}"
                    else:
                        full_url = href
                    
                    if full_url not in job_urls:
                        job_urls.append(full_url)
        
        print(f"📋 Extracted {len(job_urls)} job URLs from table\n")
        
        if not job_urls:
            print("✗ No job links found in table")
            return all_jobs
        
        # Scrape in parallel
        print(f"🔄 Scraping {len(job_urls)} jobs with {max_workers} workers...\n")
        
        success = 0
        filtered = 0
        no_email = 0
        errors = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scrape_job_detail, url): url for url in job_urls}
            
            for idx, future in enumerate(as_completed(futures), 1):
                try:
                    job = future.result()
                    if job:
                        all_jobs.append(job)
                        success += 1
                        print(f"[{idx}/{len(job_urls)}] ✓ {job['title'][:50]}")
                        print(f"                  {job['email']}\n")
                    else:
                        filtered += 1
                except Exception as e:
                    errors += 1
        
        print(f"\n{'='*70}")
        print(f"SCRAPING COMPLETE")
        print(f"{'='*70}")
        print(f"✓ Success: {success}")
        print(f"⊘ Filtered: {filtered}")
        print(f"✗ Errors: {errors}")
        print(f"📊 Total: {len(all_jobs)}")
        print(f"{'='*70}\n")
        
        return all_jobs
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return all_jobs
    finally:
        if driver:
            driver.quit()

def test_parallel_scraper():
    jobs = scrape_jobs_parallel()
    if jobs:
        print(f"✅ Found {len(jobs)} jobs:\n")
        for idx, job in enumerate(jobs[:5], 1):
            print(f"[{idx}] {job['title']}")
            print(f"    📧 {job['email']}\n")

if __name__ == "__main__":
    test_parallel_scraper()
