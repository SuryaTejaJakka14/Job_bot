"""
Parallel scraping version using ThreadPoolExecutor.
Scrapes jobs from jobs.nvoids.com/search_sph.jsp
Enhanced with detailed filtering logs and fixed ChromeDriver service.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import (
    USER_AGENT,
    DELAY_BETWEEN_SCRAPES,
    TARGET_KEYWORDS,
    EXCLUDE_KEYWORDS,
    MIN_YEARS_EXPERIENCE,
    SEARCH_KEYWORDS,
    MAX_PAGES_PER_SEARCH,
    HEADLESS_BROWSER,
    BROWSER_WAIT_TIME
)

# Set up detailed logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Additional detailed logging for filtering
filtering_logger = logging.getLogger('filtering')
filtering_logger.setLevel(logging.INFO)
filtering_handler = logging.FileHandler('logs/filtering_details.log')
filtering_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
filtering_logger.addHandler(filtering_handler)

# ============================================================
# GLOBAL CHROME SERVICE - THREAD SAFE SINGLETON
# ============================================================
CHROME_SERVICE = None

def get_chrome_service():
    """
    Get or create Chrome service (thread-safe singleton).
    Ensures ChromeDriver is only installed ONCE, not per thread.
    
    Returns:
        Service: Selenium Chrome service instance
    """
    global CHROME_SERVICE
    if CHROME_SERVICE is None:
        try:
            logging.info("Initializing ChromeDriver service...")
            CHROME_SERVICE = Service(ChromeDriverManager().install())
            logging.info("✓ ChromeDriver service initialized successfully")
        except Exception as e:
            logging.error(f"✗ Failed to initialize ChromeDriver: {str(e)}")
            raise
    return CHROME_SERVICE

def setup_driver(max_retries=3):
    """
    Set up and return a configured Chrome WebDriver with retry logic.
    Uses the singleton Chrome service to avoid multiple installations.
    
    Args:
        max_retries (int): Number of attempts to create driver (3 by default)
        
    Returns:
        WebDriver: Configured Chrome WebDriver instance
    """
    for attempt in range(max_retries):
        try:
            chrome_options = Options()
            
            # Headless mode (new, more stable)
            if HEADLESS_BROWSER:
                chrome_options.add_argument('--headless=new')
            
            # Resource-friendly options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Anti-detection
            chrome_options.add_argument(f'user-agent={USER_AGENT}')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use singleton service (CRITICAL FIX)
            service = get_chrome_service()
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logging.info(f"✓ WebDriver created successfully (attempt {attempt + 1})")
            return driver
            
        except Exception as e:
            logging.error(f"✗ Driver setup attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                logging.info(f"   Retrying in 2 seconds...")
                time.sleep(2)
            else:
                logging.error("✗ All driver setup attempts failed")
                raise
    
    return None

def extract_email(text):
    """Extract email address from text using regex."""
    if not text:
        return None
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    
    excluded_emails = [
        'usjobs@nvoids.com',
        'resumes@nvoids.com',
        'nvoids.jobs@gmail.com',
        'info@nvoids.com',
        'support@nvoids.com',
        'noreply@nvoids.com'
    ]
    
    for email in matches:
        if email.lower() not in excluded_emails:
            return email
    
    return None

def extract_years_experience(title):
    """Extract years of experience from job title."""
    patterns = [
        r'(\d+)\+\s*(?:years|yrs|yr)',
        r'(\d+)\s*(?:years|yrs|yr)',
        r'(\d+)-\d+\s*(?:years|yrs|yr)',
    ]
    
    title_lower = title.lower()
    
    for pattern in patterns:
        match = re.search(pattern, title_lower)
        if match:
            return int(match.group(1))
    
    return 0

def is_relevant_job(title, keywords=None, exclude_keywords=None, min_years=0):
    """Check if job title matches your target roles."""
    title_lower = title.lower()
    
    if keywords is None:
        keywords = TARGET_KEYWORDS
    
    if exclude_keywords is None:
        exclude_keywords = EXCLUDE_KEYWORDS
    
    # Check for excluded keywords first
    for exclude in exclude_keywords:
        if exclude.lower() in title_lower:
            return False, f"Excluded keyword '{exclude}' found in title"
    
    if not keywords:
        return True, "No filter keywords set"
    
    # Check if any target keyword is in the title
    for keyword in keywords:
        if keyword.lower() in title_lower:
            if min_years > 0:
                job_years = extract_years_experience(title)
                if job_years > 0 and job_years < min_years:
                    return False, f"Years required ({job_years}) below minimum ({min_years})"
            return True, f"Matched keyword '{keyword}'"
    
    return False, "No matching keywords found"

def scrape_job_detail_parallel(detail_url):
    """
    PARALLEL VERSION: Scrape individual job detail page.
    
    This function is designed to run in parallel using ThreadPoolExecutor.
    Each thread gets its own WebDriver instance (but uses shared service).
    
    Args:
        detail_url (str): URL of job detail page
        
    Returns:
        tuple: (job_dict, status_message) or (None, reason_filtered)
    """
    driver = None
    
    try:
        # Create a new driver for this thread (using singleton service)
        driver = setup_driver()
        driver.get(detail_url)
        
        # Wait for page to load
        time.sleep(1)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extract job title
        title_element = soup.find('table')
        if title_element:
            first_row = title_element.find('tr')
            if first_row:
                title_text = first_row.get_text(strip=True)
                if ' at ' in title_text:
                    title = title_text.split(' at ')[0].strip()
                    location = title_text.split(' at ')[1].strip()
                else:
                    title = title_text
                    location = "Not specified"
            else:
                title = "Unknown Title"
                location = "Not specified"
        else:
            title = "Unknown Title"
            location = "Not specified"
        
        # ============================================================
        # STEP 1: Check if job is relevant (by keywords/filters)
        # ============================================================
        is_relevant, relevance_reason = is_relevant_job(
            title, 
            TARGET_KEYWORDS, 
            EXCLUDE_KEYWORDS, 
            MIN_YEARS_EXPERIENCE
        )
        
        if not is_relevant:
            filtering_logger.info(f"FILTERED (Relevance): {title} | Reason: {relevance_reason}")
            return None, f"FILTERED: {relevance_reason}"
        
        # ============================================================
        # STEP 2: Extract email
        # ============================================================
        page_text = soup.get_text()
        email = extract_email(page_text)
        
        if not email:
            filtering_logger.info(f"NO EMAIL: {title} | URL: {detail_url}")
            logging.warning(f"No email found for: {title}")
            return None, "NO EMAIL FOUND"
        
        # ============================================================
        # STEP 3: Extract company from email domain
        # ============================================================
        company = "Unknown Company"
        if email:
            domain = email.split('@')[1] if '@' in email else ""
            company = domain.split('.')[0].capitalize() if domain else "Unknown Company"
        
        # Generate job ID
        job_id = detail_url.split('id=')[1].split('&')[0] if 'id=' in detail_url else detail_url
        
        job = {
            'job_id': job_id,
            'title': title,
            'company': company,
            'email': email,
            'url': detail_url,
            'location': location
        }
        
        # ============================================================
        # SUCCESS: Job passed all filters
        # ============================================================
        filtering_logger.info(f"SUCCESS: {title} | Email: {email} | Company: {company}")
        logging.info(f"✓ Scraped (parallel): {title} - {email}")
        
        return job, "SUCCESS"
        
    except Exception as e:
        logging.error(f"Error scraping {detail_url}: {str(e)}")
        filtering_logger.error(f"ERROR scraping {detail_url}: {str(e)}")
        return None, f"ERROR: {str(e)}"
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def scrape_jobs_parallel(unused_url=None, max_workers=3):
    """
    Main entry point: Scrape jobs from jobs.nvoids.com search results page.
    
    Uses the search results page (search_sph.jsp) which displays all jobs
    in a searchable/browsable format. This is much more reliable than
    trying to use a search box.
    
    Args:
        unused_url (str): Ignored (for compatibility)
        max_workers (int): Number of parallel threads for detail scraping
                          START WITH 1, increase to 2-3 if stable
                          
    Returns:
        list: Combined results of scraped jobs
    """
    all_jobs = []
    seen_job_ids = set()
    driver = None
    
    try:
        print(f"\n{'='*70}")
        print(f"AUTOMATED JOB SCRAPER - SEARCH RESULTS PAGE")
        print(f"{'='*70}")
        print(f"Target: https://jobs.nvoids.com/search_sph.jsp")
        print(f"Parallel Workers: {max_workers}")
        print(f"{'='*70}\n")
        
        # Set up driver for search results page
        driver = setup_driver()
        
        print(f"🌐 Navigating to search results page...")
        # Use the search results page directly
        driver.get("https://jobs.nvoids.com/search_sph.jsp")
        time.sleep(3)  # Wait for page to load
        
        print(f"✓ Search results page loaded")
        
        # Parse the page to extract job listings
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find all job links on the page (looking for job_details.jsp links)
        job_links = soup.find_all('a', href=re.compile(r'job_details\.jsp\?id=\d+'))
        
        print(f"\n📋 Found {len(job_links)} job links on search results page")
        
        if not job_links:
            print(f"   ✗ No job links found")
            logging.warning("No job links found on search results page")
            return all_jobs
        
        # Extract job URLs
        job_urls = []
        for link in job_links:
            href = link.get('href')
            if href.startswith('job_details.jsp'):
                full_url = f"https://jobs.nvoids.com/{href}"
            elif href.startswith('/'):
                full_url = f"https://jobs.nvoids.com{href}"
            else:
                full_url = href
            
            if full_url not in job_urls:
                job_urls.append(full_url)
        
        print(f"📌 Extracted {len(job_urls)} unique job URLs")
        
        # ============================================================
        # PARALLEL SCRAPING OF JOB DETAILS
        # ============================================================
        print(f"\n🔄 Starting parallel scraping with {max_workers} workers...")
        print(f"   Processing {len(job_urls)} job details in parallel\n")
        
        success_count = 0
        filtered_count = 0
        no_email_count = 0
        error_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(scrape_job_detail_parallel, url): url 
                for url in job_urls
            }
            
            for completed_idx, future in enumerate(as_completed(future_to_url), 1):
                url = future_to_url[future]
                
                try:
                    job, status_message = future.result()
                    
                    if job:
                        if job['job_id'] not in seen_job_ids:
                            all_jobs.append(job)
                            seen_job_ids.add(job['job_id'])
                            success_count += 1
                            print(f"   [{completed_idx}/{len(job_urls)}] ✓ SUCCESS")
                            print(f"      {job['title'][:60]}")
                            print(f"      📧 Email: {job['email']}\n")
                    else:
                        if "NO EMAIL" in status_message:
                            no_email_count += 1
                            print(f"   [{completed_idx}/{len(job_urls)}] ⚠ NO EMAIL\n")
                        else:
                            filtered_count += 1
                            print(f"   [{completed_idx}/{len(job_urls)}] ⊘ FILTERED: {status_message}\n")
                
                except Exception as e:
                    error_count += 1
                    logging.error(f"Error processing job: {str(e)}")
                    print(f"   [{completed_idx}/{len(job_urls)}] ✗ ERROR: {str(e)[:50]}\n")
        
        # ============================================================
        # FINAL STATISTICS
        # ============================================================
        print(f"\n{'='*70}")
        print(f"SCRAPING COMPLETE")
        print(f"{'='*70}")
        print(f"Total job links found: {len(job_urls)}")
        print(f"✓ Successfully scraped: {success_count}")
        print(f"⚠ No email found: {no_email_count}")
        print(f"⊘ Filtered out: {filtered_count}")
        print(f"✗ Errors: {error_count}")
        print(f"📊 Final unique jobs: {len(all_jobs)}")
        print(f"{'='*70}\n")
        
        logging.info(f"Scraping complete from search_sph.jsp: {len(all_jobs)} jobs extracted")
        
        return all_jobs
        
    except Exception as e:
        logging.error(f"Error in scrape_jobs_parallel: {str(e)}")
        print(f"   ✗ Error: {str(e)}")
        return all_jobs
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def test_parallel_scraper():
    """Test the parallel scraper."""
    print("\n" + "="*70)
    print("TESTING SEARCH RESULTS PAGE SCRAPER")
    print("="*70 + "\n")
    
    try:
        jobs = scrape_jobs_parallel(unused_url=None, max_workers=1)
        
        if jobs:
            print(f"\n{'='*70}")
            print(f"✅ SAMPLE RESULTS - First {min(10, len(jobs))} Jobs")
            print(f"{'='*70}\n")
            
            for idx, job in enumerate(jobs[:10], 1):
                print(f"[{idx}] {job['title']}")
                print(f"    📍 Location: {job['location']}")
                print(f"    🏢 Company: {job['company']}")
                print(f"    📧 Email: {job['email']}")
                print(f"    🔗 ID: {job['job_id']}")
                print("-" * 70)
        else:
            print("\n⚠ No jobs found")
    
    except Exception as e:
        logging.error(f"Test failed: {str(e)}")
        print(f"\n✗ Test failed: {str(e)}")

if __name__ == "__main__":
    test_parallel_scraper()
