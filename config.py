"""
Configuration file for job application bot.
Update these settings according to your needs.
"""

import os

# ============================================================
# EMAIL CONFIGURATION
# ============================================================

# Gmail credentials
SENDER_EMAIL = "stjakka14@gmail.com"
SENDER_PASSWORD = "cugkvqktmxexioim"  # ← UPDATE THIS

# ============================================================
# RESUME CONFIGURATION
# ============================================================

# Path to your resume file
RESUME_PATH = "/Users/suryatejajakka/desktop/marketing_workday/marketing_java/Surya_Java.docx"  # ← UPDATE THIS

# ============================================================
# APPLICATION LIMITS
# ============================================================

# Maximum number of applications to send per day
MAX_APPLICATIONS_PER_DAY = 1000

# Delay between sending each email (in seconds)
DELAY_BETWEEN_EMAILS = 10

# ============================================================
# DRY RUN MODE
# ============================================================

# Set to True for testing (no emails sent)
# Set to False for live mode (real emails sent)
DRY_RUN = True  # ← Set to False when ready to go live

# ============================================================
# PARALLEL SCRAPING CONFIGURATION
# ============================================================

# Number of parallel workers for scraping
# START WITH 1 for stability, increase to 2-3 only if stable
# Higher = faster but uses more RAM and may crash
MAX_WORKERS = 3  # ← KEEP AT 1 TO AVOID CRASHES

# ============================================================
# PAGINATION SETTINGS
# ============================================================

# Maximum number of pages to scrape per search
# Set to 1 for first page only, 5-10 for multiple pages
MAX_PAGES_TO_SCRAPE = 5

# ============================================================
# SEARCH CONFIGURATION
# ============================================================

# Keywords to search for jobs
SEARCH_KEYWORDS = ['java', 'java developer']

# Maximum pages to scrape per search keyword
MAX_PAGES_PER_SEARCH = 5

# ============================================================
# JOB FILTERING
# ============================================================

# Keywords to look for in job titles (leave empty [] to disable filtering)
TARGET_KEYWORDS = [
    'java',
    'developer',
    'engineer',
    'software',
    'full stack',
    'backend',
    'senior',
    'lead'
]

# Keywords to exclude from job titles
EXCLUDE_KEYWORDS = [
    'intern',
    'internship',
    'junior',
    'entry level',
    'student',
    'trainee'
]

# Minimum years of experience required (0 to disable)
MIN_YEARS_EXPERIENCE = 0

# ============================================================
# BROWSER CONFIGURATION
# ============================================================

# Run browser in headless mode (no GUI)
HEADLESS_BROWSER = True

# Browser wait time (seconds)
BROWSER_WAIT_TIME = 10

# User agent for web scraping
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Delay between scrapes (seconds)
DELAY_BETWEEN_SCRAPES = 2

# ============================================================
# LOGGING CONFIGURATION
# ============================================================

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# ============================================================
# VALIDATION
# ============================================================

def validate_config():
    """Validate configuration settings."""
    errors = []
    
    if not SENDER_EMAIL:
        errors.append("SENDER_EMAIL is not set")
    
    if not SENDER_PASSWORD or len(SENDER_PASSWORD) != 16:
        errors.append("SENDER_PASSWORD must be 16 characters (Gmail app password)")
    
    if not RESUME_PATH or not os.path.exists(RESUME_PATH):
        errors.append(f"RESUME_PATH does not exist: {RESUME_PATH}")
    
    if MAX_WORKERS < 1 or MAX_WORKERS > 5:
        errors.append("MAX_WORKERS must be between 1 and 5 (recommended: 1)")
    
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix these errors in config.py\n")
        return False
    
    print("✓ Configuration validated successfully")
    return True

if __name__ == "__main__":
    validate_config()
