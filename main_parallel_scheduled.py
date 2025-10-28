"""
Main file using PARALLEL scraping with ADVANCED SCHEDULING.
- Runs every 30 minutes
- Only during specified time periods (e.g., 9 AM - 6 PM)
- Auto-resets CSV after midnight
- Tracks daily limits
"""

import time
import logging
from datetime import datetime
from scraper_parallel import scrape_jobs_parallel
from email_sender import send_application
from database import (
    initialize_database,
    is_already_applied,
    is_email_already_contacted,
    record_application,
    get_application_stats,
    get_todays_application_count
)
from config import (
    DELAY_BETWEEN_EMAILS,
    MAX_APPLICATIONS_PER_DAY,
    DRY_RUN
)
from scheduler_config import (
    schedule_bot,
    should_run_now,
    is_within_working_hours,
    use_preset_business_hours,
    use_preset_extended_hours,
    use_preset_24_7,
    SCHEDULING_ENABLED
)
import pandas as pd

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def process_applications_parallel(max_workers=3):
    """
    Main job application workflow using PARALLEL scraping.
    
    Args:
        max_workers (int): Number of parallel threads (3-5 recommended)
    """
    print(f"\n{'='*70}")
    print(f"Job Application Bot - PARALLEL MODE")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print(f"Parallel Workers: {max_workers}")
    print(f"{'='*70}\n")
    
    logging.info("Starting new application cycle (PARALLEL)")
    initialize_database()
    
    today_count = get_todays_application_count()
    if today_count >= MAX_APPLICATIONS_PER_DAY:
        print(f"⚠ Daily limit reached ({today_count}/{MAX_APPLICATIONS_PER_DAY})")
        print(f"Will reset at midnight.")
        return
    
    print(f"Applications sent today: {today_count}/{MAX_APPLICATIONS_PER_DAY}\n")
    
    # ============================================================
    # PARALLEL SCRAPING HERE
    # ============================================================
    print("🔍 Starting parallel job search...\n")
    start_time = time.time()
    
    jobs = scrape_jobs_parallel(None, max_workers=max_workers)
    
    scrape_time = time.time() - start_time
    print(f"\n⏱ Scraping completed in {scrape_time:.1f} seconds")
    
    # Load applied jobs for deduplication
    print("\nLoading application history for deduplication...")
    df_applied = pd.read_csv('applied_jobs.csv')
    applied_emails = set(df_applied['email'].str.lower())
    applied_job_ids = set(df_applied['job_id'])
    
    # Filter jobs
    filtered_jobs = []
    for job in jobs:
        if job['job_id'] in applied_job_ids:
            continue
        if job['email'].lower() in applied_emails:
            continue
        filtered_jobs.append(job)
    
    print(f"After deduplication: {len(filtered_jobs)} unique applications\n")
    
    total_applied = 0
    
    # ============================================================
    # Send applications (sequential - unavoidable)
    # ============================================================
    print("📧 Sending applications...\n")
    
    for job in filtered_jobs:
        if get_todays_application_count() >= MAX_APPLICATIONS_PER_DAY:
            print(f"\n⚠ Daily limit reached during cycle ({MAX_APPLICATIONS_PER_DAY})")
            print(f"Will resume at next scheduled time or after midnight reset.")
            break
        
        print(f"→ {job['title'][:50]}")
        success = send_application(job['title'], job['company'], job['email'])
        record_application(job['job_id'], job['title'], job['company'], job['email'])
        
        if success:
            total_applied += 1
        
        time.sleep(DELAY_BETWEEN_EMAILS)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"Cycle Complete")
    print(f"{'='*70}")
    print(f"Jobs found: {len(jobs)}")
    print(f"Unique jobs: {len(filtered_jobs)}")
    print(f"Applications sent: {total_applied}")
    print(f"Scraping time: {scrape_time:.1f} seconds")
    
    # Overall statistics
    stats = get_application_stats()
    print(f"\nOverall Statistics (All Time):")
    print(f"  Total applications: {stats['total']}")
    print(f"  Successfully sent: {stats['sent']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Unique emails contacted: {stats['unique_emails']}")
    print(f"{'='*70}\n")
    
    logging.info(f"Parallel cycle complete: {total_applied} sent in {scrape_time:.1f}s scrape time")

def run_once_parallel():
    """Run once with parallel scraping (for testing)."""
    print("\n🤖 Running Job Application Bot (PARALLEL MODE - ONCE)\n")
    process_applications_parallel(max_workers=3)

def run_scheduled_parallel():
    """Run scheduled with parallel scraping and advanced scheduling."""
    print("\n🤖 Job Application Bot Started (PARALLEL MODE - SCHEDULED)\n")
    
    # Pass the process function to the scheduler
    schedule_bot(process_applications_parallel)

def show_schedule_status():
    """Display current scheduling status."""
    print("\n" + "="*70)
    print("SCHEDULING STATUS")
    print("="*70)
    print(f"Scheduling Enabled: {'YES' if SCHEDULING_ENABLED else 'NO'}")
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S (%A)')}")
    print(f"Within Working Hours: {'YES' if is_within_working_hours() else 'NO'}")
    print(f"Should Run Now: {'YES' if should_run_now() else 'NO'}")
    print("="*70 + "\n")

if __name__ == "__main__":
    # ============================================================
    # CHOOSE YOUR MODE - UNCOMMENT ONE OF THESE
    # ============================================================
    
    # Mode 1: RUN ONCE (for testing)
    #run_once_parallel()
    
    # Mode 2: RUN WITH SCHEDULING (24/7 automation)
    use_preset_business_hours()  # Optional: set working hours
    run_scheduled_parallel()
    
    # Mode 3: SHOW STATUS AND DECIDE
    # show_schedule_status()
    # if should_run_now():
    #     print("✓ Within working hours - running now...\n")
    #     process_applications_parallel(max_workers=3)
    # else:
    #     print("⊘ Outside working hours - not running.")
