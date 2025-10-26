import schedule
import time
import logging
from datetime import datetime
from scraper import scrape_jobs
from email_sender import send_application
from database import (
    initialize_database,
    is_already_applied,
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

# ============================================================
# CONFIGURE YOUR JOB BOARD URLs HERE
# ============================================================
JOB_URLS = [
   'https://jobs.nvoids.com/index.jsp',  # Main page - latest jobs
    'https://jobs.nvoids.com/index.jsp?p=1',  # Page 2
    'https://jobs.nvoids.com/index.jsp?p=2',  # Page 3
]

def process_applications():
    """Main job application workflow."""
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
    
    # Check if URLs are configured
    if not JOB_URLS:
        print("⚠ No job board URLs configured!")
        print("Please add URLs to the JOB_URLS list in main.py")
        logging.warning("No job URLs configured")
        return
    
    total_found = 0
    total_applied = 0
    total_skipped = 0
    
    # Process each job board URL
    for url in JOB_URLS:
        print(f"\n📋 Scraping: {url}")
        logging.info(f"Processing URL: {url}")
        
        jobs = scrape_jobs(url)
        print(f"   Found {len(jobs)} jobs with email addresses\n")
        total_found += len(jobs)
        
        # Process each job
        for job in jobs:
            job_id = job['job_id']
            
            # Check if already applied
            if is_already_applied(job_id):
                print(f"   ⊘ Skipped: {job['title']} at {job['company']} (already applied)")
                total_skipped += 1
                continue
            
            # Check daily limit again
            if get_todays_application_count() >= MAX_APPLICATIONS_PER_DAY:
                print(f"\n⚠ Daily limit reached during cycle")
                logging.warning("Daily limit reached mid-cycle")
                break
            
            # Send application
            print(f"   → Applying: {job['title']} at {job['company']}")
            success = send_application(
                job['title'],
                job['company'],
                job['email']
            )
            
            # Record application
            status = 'sent' if success else 'failed'
            record_application(
                job_id,
                job['title'],
                job['company'],
                job['email'],
                status
            )
            
            if success:
                total_applied += 1
            
            # Rate limiting
            print(f"   ⏱ Waiting {DELAY_BETWEEN_EMAILS} seconds before next email...")
            time.sleep(DELAY_BETWEEN_EMAILS)
    
    # Print summary
    print(f"\n{'='*70}")
    print("Cycle Complete - Summary")
    print(f"{'='*70}")
    print(f"Jobs found with emails: {total_found}")
    print(f"Applications sent: {total_applied}")
    print(f"Already applied (skipped): {total_skipped}")
    
    # Overall stats
    stats = get_application_stats()
    print(f"\nOverall Statistics:")
    print(f"  Total applications: {stats['total']}")
    print(f"  Successfully sent: {stats['sent']}")
    print(f"  Failed: {stats['failed']}")
    print(f"{'='*70}\n")
    
    logging.info(f"Cycle complete: {total_applied} sent, {total_skipped} skipped")

def run_once():
    """Run the bot once (for testing)."""
    print("\n🤖 Running Job Application Bot (Single Run)\n")
    process_applications()

def run_scheduled():
    """Run the bot on a schedule."""
    print("\n🤖 Job Application Bot Started")
    print("📅 Schedule: Every 30 minutes")
    print("⏹ Press Ctrl+C to stop\n")
    
    # Run immediately on start
    process_applications()
    
    # Schedule every 30 minutes
    schedule.every(30).minutes.do(process_applications)
    
    logging.info("Scheduler started - running every 30 minutes")
    
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
