import schedule
import time
import logging
from datetime import datetime
from scraper import scrape_jobs
from email_sender import send_application
from database import (
    initialize_database,
    is_already_applied,
    is_email_already_contacted,  # ← Email deduplication
    record_application,
    get_application_stats,
    get_todays_application_count
)
from config import (
    DELAY_BETWEEN_EMAILS,
    MAX_APPLICATIONS_PER_DAY,
    DRY_RUN
)

# Set up logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def process_applications():
    """Main job application workflow with email-based deduplication."""
    print(f"\n{'='*70}")
    print(f"Job Application Bot - Cycle Started")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print(f"{'='*70}\n")
    
    logging.info("="*70)
    logging.info("Starting new application cycle")
    
    # Initialize database
    initialize_database()
    
    # Check daily limit
    today_count = get_todays_application_count()
    if today_count >= MAX_APPLICATIONS_PER_DAY:
        print(f"⚠ Daily limit reached ({today_count}/{MAX_APPLICATIONS_PER_DAY})")
        print("Skipping this cycle.")
        logging.warning(f"Daily limit reached: {today_count}/{MAX_APPLICATIONS_PER_DAY}")
        return
    
    print(f"Applications sent today: {today_count}/{MAX_APPLICATIONS_PER_DAY}\n")
    
    total_found = 0
    total_applied = 0
    total_skipped_job_id = 0
    total_skipped_email = 0
    
    # ============================================================
    # SEARCH-BASED SCRAPING (uses SEARCH_KEYWORDS from config.py)
    # ============================================================
    print("🔍 Starting automated job search...\n")
    
    # Call scraper - it will use Selenium to search with configured keywords
    jobs = scrape_jobs(None)  # Pass None - scraper uses SEARCH_KEYWORDS internally
    
    total_found = len(jobs)
    print(f"\n{'='*70}")
    print(f"Search Complete: Found {total_found} relevant jobs")
    print(f"{'='*70}\n")
    
    if total_found == 0:
        print("⚠ No jobs found. Check:")
        print("  1. SEARCH_KEYWORDS in config.py")
        print("  2. TARGET_KEYWORDS filtering (might be too strict)")
        print("  3. Website accessibility")
        print("  4. Internet connection")
        return
    
    print(f"Processing {total_found} jobs for applications...\n")
    
    # Process each job
    for job in jobs:
        job_id = job['job_id']
        email = job['email'].lower()
        
        # ============================================================
        # CHECK 1: Job ID Duplication
        # ============================================================
        if is_already_applied(job_id):
            print(f"   ⊘ Skipped: {job['title'][:50]}... (job ID {job_id} already applied)")
            total_skipped_job_id += 1
            continue
        
        # ============================================================
        # CHECK 2: Email Duplication
        # ============================================================
        if is_email_already_contacted(email):
            print(f"   ⊘ Skipped: {job['title'][:50]}... (email {email} already contacted)")
            total_skipped_email += 1
            continue
        
        # ============================================================
        # CHECK 3: Daily Limit
        # ============================================================
        if get_todays_application_count() >= MAX_APPLICATIONS_PER_DAY:
            print(f"\n⚠ Daily limit reached during cycle ({MAX_APPLICATIONS_PER_DAY})")
            logging.warning("Daily limit reached mid-cycle")
            break
        
        # ============================================================
        # ALL CHECKS PASSED: Send Application
        # ============================================================
        print(f"\n   → Applying to Job #{total_applied + 1}")
        print(f"      Title: {job['title'][:60]}")
        print(f"      Company: {job['company']}")
        print(f"      Email: {email}")
        
        success = send_application(
            job['title'],
            job['company'],
            email
        )
        
        # Record application
        status = 'sent' if success else 'failed'
        record_application(
            job_id,
            job['title'],
            job['company'],
            email,
            status
        )
        
        if success:
            total_applied += 1
            print(f"      ✓ Status: Application sent")
        else:
            print(f"      ✗ Status: Failed to send")
        
        # Rate limiting
        if total_applied < MAX_APPLICATIONS_PER_DAY:
            print(f"      ⏱ Waiting {DELAY_BETWEEN_EMAILS} seconds...")
            time.sleep(DELAY_BETWEEN_EMAILS)
    
    # Print comprehensive summary
    print(f"\n{'='*70}")
    print("Cycle Complete - Summary")
    print(f"{'='*70}")
    print(f"\nJobs Found: {total_found}")
    print(f"Applications Sent: {total_applied}")
    print(f"Skipped (duplicate job ID): {total_skipped_job_id}")
    print(f"Skipped (duplicate email): {total_skipped_email}")
    print(f"Total Skipped: {total_skipped_job_id + total_skipped_email}")
    
    # Overall statistics
    stats = get_application_stats()
    print(f"\nOverall Statistics (All Time):")
    print(f"  Total applications: {stats['total']}")
    print(f"  Successfully sent: {stats['sent']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Unique emails contacted: {stats['unique_emails']}")
    print(f"{'='*70}\n")
    
    logging.info(f"Cycle complete: {total_applied} sent, {total_skipped_job_id} skipped (job ID), {total_skipped_email} skipped (email)")

def run_once():
    """Run the bot once (for testing)."""
    print("\n🤖 Running Job Application Bot (Single Run)\n")
    process_applications()

def run_scheduled():
    """Run the bot on a schedule."""
    print("\n🤖 Job Application Bot Started")
    print("📅 Schedule: Every 2 hours")
    print("⏹ Press Ctrl+C to stop\n")
    
    # Run immediately on start
    process_applications()
    
    # Schedule every 2 hours (recommended for Selenium)
    schedule.every(2).hours.do(process_applications)
    
    logging.info("Scheduler started - running every 2 hours")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n⏹ Bot stopped by user")
        logging.info("Bot stopped by user")

if __name__ == "__main__":
    # Choose mode:
    # 1. Run once for testing
    run_once()
    
    # 2. Run on schedule (uncomment to use)
    # run_scheduled()
