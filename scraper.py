"""
Scraper for jobs.nvoids.com with automated search functionality.
Uses Selenium to automate browser interaction with the search box.
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

# Set up logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    chrome_options = Options()
    
    if HEADLESS_BROWSER:
        chrome_options.add_argument('--headless')  # Run without GUI
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'user-agent={USER_AGENT}')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Automatically download and set up ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    logging.info("Chrome WebDriver initialized")
    return driver

def extract_email(text):
    """Extract email address from text using regex."""
    if not text:
        return None
    
    # Email regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    
    # Filter out common generic/bot emails
    excluded_emails = [
        'usjobs@nvoids.com',
        'resumes@nvoids.com',
        'nvoids.jobs@gmail.com',
        'info@nvoids.com',
        'support@nvoids.com'
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
            logging.info(f"Filtered out (excluded keyword '{exclude}'): {title}")
            return False
    
    # If no filter keywords set, accept all jobs
    if not keywords:
        return True
    
    # Check if any target keyword is in the title
    matched_keyword = None
    for keyword in keywords:
        if keyword.lower() in title_lower:
            matched_keyword = keyword
            break
    
    if not matched_keyword:
        logging.info(f"Filtered out (no matching keywords): {title}")
        return False
    
    # Check years of experience
    if min_years > 0:
        job_years = extract_years_experience(title)
        if job_years > 0 and job_years < min_years:
            logging.info(f"Filtered out (requires {job_years} years, minimum is {min_years}): {title}")
            return False
    
    logging.info(f"Job accepted (matched keyword '{matched_keyword}'): {title}")
    return True

def search_jobs_on_nvoids(driver, search_keyword):
    """
    Perform a search on jobs.nvoids.com using Selenium.
    
    Args:
        driver: Selenium WebDriver instance
        search_keyword: Keyword to search for (e.g., 'java developer')
        
    Returns:
        bool: True if search was successful
    """
    try:
        print(f"\n   Navigating to jobs.nvoids.com...")
        driver.get("https://jobs.nvoids.com")
        logging.info(f"Navigated to jobs.nvoids.com")
        
        # Wait for page to load
        time.sleep(2)
        
        # Find the search box - try multiple possible selectors
        print(f"   Looking for search box...")
        search_box = None
        
        # Try common search input selectors
        search_selectors = [
            (By.NAME, "keyword"),
            (By.NAME, "search"),
            (By.ID, "keyword"),
            (By.ID, "search"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input[placeholder*='search' i]"),
            (By.CSS_SELECTOR, "input[placeholder*='keyword' i]"),
            (By.XPATH, "//input[@type='text']"),
        ]
        
        for selector_type, selector_value in search_selectors:
            try:
                search_box = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                print(f"   ✓ Found search box using {selector_type}: {selector_value}")
                break
            except:
                continue
        
        if not search_box:
            logging.error("Search box not found on page")
            print("   ✗ Could not find search box")
            return False
        
        # Clear the search box and enter keyword
        print(f"   Entering search keyword: '{search_keyword}'")
        search_box.clear()
        search_box.send_keys(search_keyword)
        time.sleep(1)
        
        # Submit the search (press Enter)
        print(f"   Submitting search...")
        search_box.send_keys(Keys.RETURN)
        
        # Wait for results to load
        time.sleep(3)
        
        logging.info(f"Search completed for keyword: {search_keyword}")
        print(f"   ✓ Search results loaded")
        
        return True
        
    except Exception as e:
        logging.error(f"Error performing search for '{search_keyword}': {str(e)}")
        print(f"   ✗ Search error: {str(e)}")
        return False

def get_job_detail_urls_from_current_page(driver):
    """
    Extract job detail URLs from the current page (after search).
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        list: List of job detail page URLs
    """
    job_urls = []
    
    try:
        # Get page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find all job links
        links = soup.find_all('a', href=re.compile(r'job_details\.jsp\?id=\d+'))
        
        for link in links:
            href = link.get('href')
            
            # Build full URL
            if href.startswith('job_details.jsp'):
                full_url = f"https://jobs.nvoids.com/{href}"
            elif href.startswith('/'):
                full_url = f"https://jobs.nvoids.com{href}"
            else:
                full_url = href
            
            if full_url not in job_urls:
                job_urls.append(full_url)
        
        logging.info(f"Found {len(job_urls)} job URLs on current page")
        
        return job_urls
        
    except Exception as e:
        logging.error(f"Error extracting job URLs: {str(e)}")
        return []

def scrape_job_detail(driver, detail_url):
    """
    Scrape individual job detail page.
    
    Args:
        driver: Selenium WebDriver instance
        detail_url: URL of job detail page
        
    Returns:
        dict: Job information or None
    """
    try:
        driver.get(detail_url)
        time.sleep(2)  # Wait for page to load
        
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
        
        # Apply filtering
        if not is_relevant_job(title, TARGET_KEYWORDS, EXCLUDE_KEYWORDS, MIN_YEARS_EXPERIENCE):
            return None
        
        # Extract email
        page_text = soup.get_text()
        email = extract_email(page_text)
        
        if not email:
            logging.warning(f"No email found for: {title}")
            return None
        
        # Extract company from email domain
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
        
        logging.info(f"✓ Scraped: {title} - {email}")
        return job
        
    except Exception as e:
        logging.error(f"Error scraping {detail_url}: {str(e)}")
        return None

def scrape_jobs_with_search(search_keyword):
    """
    Main function: Search for jobs and scrape results.
    
    Args:
        search_keyword: Keyword to search for (e.g., 'java developer')
        
    Returns:
        list: List of job dictionaries
    """
    jobs = []
    driver = None
    
    try:
        print(f"\n{'='*70}")
        print(f"SEARCHING FOR: '{search_keyword}'")
        print(f"{'='*70}")
        
        # Set up browser
        driver = setup_driver()
        
        # Perform search
        search_success = search_jobs_on_nvoids(driver, search_keyword)
        
        if not search_success:
            print(f"   ✗ Search failed for '{search_keyword}'")
            return jobs
        
        # Scrape multiple pages
        for page_num in range(MAX_PAGES_PER_SEARCH):
            print(f"\n   --- Page {page_num + 1} of {MAX_PAGES_PER_SEARCH} ---")
            
            # Get job URLs from current page
            job_urls = get_job_detail_urls_from_current_page(driver)
            
            if not job_urls:
                print(f"   No more jobs found on page {page_num + 1}")
                break
            
            print(f"   Found {len(job_urls)} job postings on this page")
            print(f"   Processing job details...")
            
            # Scrape each job
            for idx, job_url in enumerate(job_urls, 1):
                if idx % 10 == 0:
                    print(f"      Progress: {idx}/{len(job_urls)}...")
                
                job = scrape_job_detail(driver, job_url)
                
                if job:
                    jobs.append(job)
                    print(f"      ✓ [{len(jobs)}] {job['title'][:50]}... - {job['email']}")
                
                time.sleep(DELAY_BETWEEN_SCRAPES)
            
            # Go to next page if available
            if page_num < MAX_PAGES_PER_SEARCH - 1:
                try:
                    print(f"\n   Navigating to next page...")
                    # Look for "Next" button or page link
                    next_button = driver.find_element(By.LINK_TEXT, "Next")
                    next_button.click()
                    time.sleep(3)
                except:
                    print(f"   No 'Next' button found - end of results")
                    break
        
        print(f"\n{'='*70}")
        print(f"   Search '{search_keyword}' complete: {len(jobs)} relevant jobs found")
        print(f"{'='*70}")
        
        logging.info(f"Completed search for '{search_keyword}': {len(jobs)} jobs")
        
        return jobs
        
    except Exception as e:
        logging.error(f"Error in scrape_jobs_with_search: {str(e)}")
        print(f"   ✗ Error: {str(e)}")
        return jobs
        
    finally:
        if driver:
            driver.quit()
            logging.info("Browser closed")

def scrape_jobs(unused_url=None):
    """
    Main entry point called by main.py.
    Performs searches for all configured keywords.
    
    Args:
        unused_url: Ignored (for compatibility with main.py)
        
    Returns:
        list: Combined results from all searches
    """
    all_jobs = []
    seen_job_ids = set()
    
    print(f"\n{'='*70}")
    print(f"AUTOMATED JOB SEARCH BOT")
    print(f"{'='*70}")
    print(f"Search Keywords: {SEARCH_KEYWORDS}")
    print(f"Max Pages per Search: {MAX_PAGES_PER_SEARCH}")
    print(f"Headless Mode: {HEADLESS_BROWSER}")
    print(f"{'='*70}\n")
    
    for keyword in SEARCH_KEYWORDS:
        print(f"\n🔍 Starting search #{SEARCH_KEYWORDS.index(keyword) + 1}/{len(SEARCH_KEYWORDS)}")
        
        jobs = scrape_jobs_with_search(keyword)
        
        # Remove duplicates
        for job in jobs:
            if job['job_id'] not in seen_job_ids:
                all_jobs.append(job)
                seen_job_ids.add(job['job_id'])
        
        print(f"   Total unique jobs so far: {len(all_jobs)}")
        
        # Wait between searches
        if keyword != SEARCH_KEYWORDS[-1]:
            print(f"   Waiting before next search...")
            time.sleep(5)
    
    print(f"\n{'='*70}")
    print(f"ALL SEARCHES COMPLETE")
    print(f"{'='*70}")
    print(f"Total keywords searched: {len(SEARCH_KEYWORDS)}")
    print(f"Total unique jobs found: {len(all_jobs)}")
    print(f"{'='*70}\n")
    
    return all_jobs

def test_scraper():
    """Test the scraper with one search."""
    print("\n" + "="*70)
    print("TESTING SELENIUM-BASED SCRAPER")
    print("="*70 + "\n")
    
    print("Configuration:")
    print(f"  Search Keywords: {SEARCH_KEYWORDS}")
    print(f"  Headless Browser: {HEADLESS_BROWSER}")
    print(f"  Max Pages per Search: {MAX_PAGES_PER_SEARCH}")
    print()
    
    # Test with first search keyword only
    test_keyword = SEARCH_KEYWORDS[0] if SEARCH_KEYWORDS else "java developer"
    
    print(f"Testing with keyword: '{test_keyword}'")
    print("(To test all keywords, run main.py instead)\n")
    
    jobs = scrape_jobs_with_search(test_keyword)
    
    if jobs:
        print(f"\n{'='*70}")
        print(f"SAMPLE RESULTS - First {min(5, len(jobs))} Jobs")
        print(f"{'='*70}\n")
        
        for idx, job in enumerate(jobs[:5], 1):
            print(f"[{idx}] {job['title']}")
            print(f"    Company: {job['company']}")
            print(f"    Email: {job['email']}")
            print(f"    Location: {job['location']}")
            print("-" * 70)
        
        if len(jobs) > 5:
            print(f"\n... and {len(jobs) - 5} more jobs")
    else:
        print("\n⚠ No jobs found. Check:")
        print("  1. Internet connection")
        print("  2. Website is accessible")
        print("  3. Search keyword is valid")
        print("  4. Filter settings in config.py")

if __name__ == "__main__":
    test_scraper()
