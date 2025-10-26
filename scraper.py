import requests
from bs4 import BeautifulSoup
import re
import logging
import time
from config import (
    USER_AGENT, 
    DELAY_BETWEEN_SCRAPES,
    TARGET_KEYWORDS,
    EXCLUDE_KEYWORDS,
    MIN_YEARS_EXPERIENCE
)

# Set up logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
    """
    Extract years of experience from job title.
    Examples: "5+ years", "7-10 years", "10+ yrs", "Senior (8+ years)"
    
    Args:
        title (str): Job title
        
    Returns:
        int: Minimum years required, or 0 if not found
    """
    # Patterns for years: "5+", "7-10", "8+ years", etc.
    patterns = [
        r'(\d+)\+\s*(?:years|yrs|yr)',  # "5+ years"
        r'(\d+)\s*(?:years|yrs|yr)',     # "5 years"
        r'(\d+)-\d+\s*(?:years|yrs|yr)', # "7-10 years" (take min)
    ]
    
    title_lower = title.lower()
    
    for pattern in patterns:
        match = re.search(pattern, title_lower)
        if match:
            return int(match.group(1))
    
    return 0

def is_relevant_job(title, keywords=None, exclude_keywords=None, min_years=0):
    """
    Check if job title matches your target roles.
    
    Args:
        title (str): Job title
        keywords (list): Keywords you're interested in (from config)
        exclude_keywords (list): Keywords to exclude
        min_years (int): Minimum years of experience required
        
    Returns:
        bool: True if job is relevant
    """
    title_lower = title.lower()
    
    # Use config keywords if not provided
    if keywords is None:
        keywords = TARGET_KEYWORDS
    
    if exclude_keywords is None:
        exclude_keywords = EXCLUDE_KEYWORDS
    
    # Check for excluded keywords first (immediate disqualification)
    for exclude in exclude_keywords:
        if exclude.lower() in title_lower:
            logging.info(f"Filtered out (excluded keyword '{exclude}'): {title}")
            return False
    
    # If no filter keywords set, accept all jobs (after exclusions)
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
    
    # Check years of experience if min_years is set
    if min_years > 0:
        job_years = extract_years_experience(title)
        if job_years > 0 and job_years < min_years:
            logging.info(f"Filtered out (requires {job_years} years, minimum is {min_years}): {title}")
            return False
    
    logging.info(f"Job accepted (matched keyword '{matched_keyword}'): {title}")
    return True

def get_job_detail_urls(main_page_url):
    """
    Step 1: Extract job detail page URLs from the main listing page.
    
    Args:
        main_page_url (str): URL of the main jobs listing page
        
    Returns:
        list: List of job detail page URLs
    """
    headers = {'User-Agent': USER_AGENT}
    job_urls = []
    
    try:
        logging.info(f"Fetching job list from: {main_page_url}")
        response = requests.get(main_page_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all job links in the table
        # Jobs are in table rows with links to job_details.jsp
        links = soup.find_all('a', href=re.compile(r'job_details\.jsp\?id=\d+'))
        
        for link in links:
            href = link.get('href')
            
            # Build full URL if it's relative
            if href.startswith('job_details.jsp'):
                full_url = f"https://jobs.nvoids.com/{href}"
            elif href.startswith('/'):
                full_url = f"https://jobs.nvoids.com{href}"
            else:
                full_url = href
            
            if full_url not in job_urls:
                job_urls.append(full_url)
        
        logging.info(f"Found {len(job_urls)} job detail URLs")
        print(f"   Found {len(job_urls)} job postings on page")
        
        return job_urls
    
    except Exception as e:
        logging.error(f"Error fetching job URLs from {main_page_url}: {str(e)}")
        print(f"   Error: {str(e)}")
        return []

def scrape_job_detail(detail_url):
    """
    Step 2: Scrape individual job detail page for email and job info.
    
    Args:
        detail_url (str): URL of the job detail page
        
    Returns:
        dict: Job information including email, or None if no email found or filtered out
    """
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = requests.get(detail_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract job title (usually in the first table row or header)
        title_element = soup.find('table')
        if title_element:
            first_row = title_element.find('tr')
            if first_row:
                title_text = first_row.get_text(strip=True)
                # Title usually ends with "at [Location]"
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
        # APPLY FILTERING BEFORE EXTRACTING EMAIL (save bandwidth)
        # ============================================================
        if not is_relevant_job(title, TARGET_KEYWORDS, EXCLUDE_KEYWORDS, MIN_YEARS_EXPERIENCE):
            return None  # Skip this job - not relevant
        
        # Extract email from the entire page content
        page_text = soup.get_text()
        email = extract_email(page_text)
        
        # Extract company name (not always available, try to find from email domain)
        company = "Unknown Company"
        if email:
            domain = email.split('@')[1] if '@' in email else ""
            company = domain.split('.')[0].capitalize() if domain else "Unknown Company"
        
        # Generate unique job ID from URL
        job_id = detail_url.split('id=')[1].split('&')[0] if 'id=' in detail_url else detail_url
        
        if email:
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
        else:
            logging.warning(f"⊘ No email found for job: {title}")
            return None
    
    except Exception as e:
        logging.error(f"Error scraping {detail_url}: {str(e)}")
        return None

def scrape_jobs(main_url):
    """
    Main scraping function for jobs.nvoids.com
    
    This function:
    1. Gets all job detail page URLs from the main listing
    2. Visits each detail page to extract email and job info
    3. Filters jobs based on keywords and criteria
    
    Args:
        main_url (str): URL of the main jobs listing page
        
    Returns:
        list: List of job dictionaries with email addresses (filtered)
    """
    jobs = []
    filtered_count = 0
    no_email_count = 0
    
    print(f"\n{'='*70}")
    print(f"Scraping: {main_url}")
    print(f"{'='*70}")
    
    # Step 1: Get all job detail URLs
    job_detail_urls = get_job_detail_urls(main_url)
    
    if not job_detail_urls:
        print("   No job URLs found on this page")
        return jobs
    
    # Step 2: Scrape each job detail page with filtering
    print(f"   Processing {len(job_detail_urls)} job postings...")
    print(f"   Filtering enabled: {len(TARGET_KEYWORDS)} keywords")
    
    for idx, detail_url in enumerate(job_detail_urls, 1):
        # Simplified progress indicator
        if idx % 10 == 0:
            print(f"   Progress: {idx}/{len(job_detail_urls)} processed...")
        
        job = scrape_job_detail(detail_url)
        
        if job:
            jobs.append(job)
            print(f"      ✓ [{idx}] {job['title'][:50]}... - {job['email']}")
        else:
            # Check if it was filtered or had no email
            # (This is already logged in the functions above)
            pass
        
        # Be polite - wait between requests
        time.sleep(DELAY_BETWEEN_SCRAPES)
    
    print(f"\n{'='*70}")
    print(f"   Results Summary:")
    print(f"   - Total postings checked: {len(job_detail_urls)}")
    print(f"   - Relevant jobs found: {len(jobs)}")
    print(f"   - Filter rate: {((len(job_detail_urls) - len(jobs)) / len(job_detail_urls) * 100):.1f}%")
    print(f"{'='*70}\n")
    
    logging.info(f"Successfully scraped {len(jobs)} relevant jobs from {main_url}")
    
    return jobs

def test_scraper():
    """Test the scraper with jobs.nvoids.com"""
    print("\n" + "="*70)
    print("TESTING NVOIDS.COM SCRAPER WITH FILTERING")
    print("="*70 + "\n")
    
    print("Filter Configuration:")
    print(f"  - Target Keywords: {TARGET_KEYWORDS[:5]}..." if len(TARGET_KEYWORDS) > 5 else f"  - Target Keywords: {TARGET_KEYWORDS}")
    print(f"  - Exclude Keywords: {EXCLUDE_KEYWORDS[:5]}..." if len(EXCLUDE_KEYWORDS) > 5 else f"  - Exclude Keywords: {EXCLUDE_KEYWORDS}")
    print(f"  - Minimum Years: {MIN_YEARS_EXPERIENCE}")
    print()
    
    test_url = "https://jobs.nvoids.com/index.jsp"
    jobs = scrape_jobs(test_url)
    
    if jobs:
        print(f"\n{'='*70}")
        print(f"SAMPLE RESULTS - First {min(5, len(jobs))} Jobs")
        print(f"{'='*70}\n")
        
        # Show first 5 jobs
        for idx, job in enumerate(jobs[:5], 1):
            print(f"[{idx}] Job ID: {job['job_id']}")
            print(f"    Title: {job['title']}")
            print(f"    Company: {job['company']}")
            print(f"    Location: {job['location']}")
            print(f"    Email: {job['email']}")
            print(f"    URL: {job['url'][:60]}...")
            print("-" * 70)
        
        if len(jobs) > 5:
            print(f"\n... and {len(jobs) - 5} more jobs\n")
    else:
        print("\n⚠ No relevant jobs found matching your criteria.")
        print("   Try:")
        print("   1. Broadening your TARGET_KEYWORDS in config.py")
        print("   2. Removing some EXCLUDE_KEYWORDS")
        print("   3. Lowering MIN_YEARS_EXPERIENCE")
        print("   4. Checking if the website is accessible")

# Test function
if __name__ == "__main__":
    test_scraper()
