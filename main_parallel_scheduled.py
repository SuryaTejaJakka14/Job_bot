"""
Main file using PARALLEL scraping with ADVANCED SCHEDULING.
- Runs every 30 minutes
- Only during specified time periods (9 AM - 10 PM PST)
- Auto-resets CSV after midnight / at EOD
- Tracks daily limits
- DELETES CSV at EOD (10 PM PST)
"""

import time
import logging
import os
from datetime import datetime
from pytz import timezone as tz
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
    DRY_RUN,
    MAX_WORKERS,
    MAX_PAGES_TO_SCRAPE
)
from scheduler_config import (
    schedule_bot,
    should_run_now,
    is_within_working_hours,
    use_preset_business_hours,
    SCHEDULING_ENABLED
)
import pandas as pd

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Timezone
PST = tz('America/Los_Angeles')

# ============================================================
# CSV FILE MANAGEMENT
# ============================================================

CSV_FILE = 'applied_jobs.csv'
EOD_HOUR = 23  # 10 PM - End of day
EOD_MINUTE = 0

def get_current_pst_time():
    """Get current time in PST."""
    return datetime.now(PST)

def is_eod():
    """Check if it's End Of Day (10 PM PST or later)."""
    now = get_current_pst_time()
    return now.hour >= EOD_HOUR and now.minute >= EOD_MINUTE

def reset_csv_file():
    """Reset (delete) the CSV file at EOD."""
    try:
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
            logging.info(f"✓ CSV file deleted at EOD: {CSV_FILE}")
            print(f"\n✓ CSV file deleted at EOD: {CSV_FILE}")
            
            # Recreate header for next day
            initialize_database()
            print(f"✓ CSV file recreated with headers for next day\n")
            logging.info("✓ CSV file recreated with headers")
        else:
            logging.info(f"CSV file not found: {CSV_FILE}")
    except Exception as e:
        logging.error(f"✗ Error deleting CSV file: {str(e)}")
        print(f"✗ Error deleting CSV file: {str(e)}")

def backup_csv_file():
    """Backup the current CSV file before deleting it."""
    try:
        if os.path.exists(CSV_FILE):
            now = get_current_pst_time()
            backup_name = f"applied_jobs_backup_{now.strftime('%Y-%m-%d')}.csv"
            
            with open(CSV_FILE, 'r') as source:
                with open(backup_name, 'w') as dest:
                    dest.write(source.read())
            
            logging.info(f"✓ CSV backed up to: {backup_name}")
            print(f"✓ CSV backed up to: {backup_name}")
    except Exception as e:
        logging.error(f"Error backing up CSV: {str(e)}")

def process_applications_parallel(max_workers=None, max_pages=None):
    """
    Main job application workflow using PARALLEL scraping.
    Checks for EOD and deletes CSV if needed.
    """
    if max_workers is None:
        max_workers = MAX_WORKERS
    
    if max_pages is None:
        max_pages = MAX_PAGES_TO_SCRAPE
    
    now_pst = get_current_pst_time()
    
    print(f"\n{'='*70}")
    print(f"Job Application Bot - PARALLEL MODE")
    print(f"{'='*70}")
    print(f"Time (PST): {now_pst.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print(f"Parallel Workers: {max_workers}")
    print(f"Max Pages: {max_pages}")
    print(f"{'='*70}\n")
    
    logging.info(f"Starting cycle at {now_pst}")
    
    # ============================================================
    # CHECK IF EOD - DELETE CSV IF NEEDED
    # ============================================================
    if is_eod():
        print(f"\n⏰ END OF DAY DETECTED ({EOD_HOUR}:{EOD_MINUTE:02d} PST)")
        print(f"   Backing up and deleting CSV file...\n")
        
        backup_csv_file()
        reset_csv_file()
        
        logging.info("End of day reached - CSV file reset")
        return
    
    # ============================================================
    # NORMAL APPLICATION PROCESSING
    # ============================================================
    initialize_database()
    
    today_count = get_todays_application_count()
    if today_count >= MAX_APPLICATIONS_PER_DAY:
        print(f"⚠ Daily limit reached ({today_count}/{MAX_APPLICATIONS_PER_DAY})")
        print(f"Will reset at EOD.")
        return
    
    print(f"Applications sent today: {today_count}/{MAX_APPLICATIONS_PER_DAY}\n")
    
    # ============================================================
    # PARALLEL SCRAPING
    # ============================================================
    print("🔍 Starting parallel job search...\n")
    start_time = time.time()
    
    jobs = scrape_jobs_parallel(None, max_workers=max_workers, max_pages=max_pages)
    
    scrape_time = time.time() - start_time
    print(f"\n⏱ Scraping completed in {scrape_time:.1f} seconds")
    
    if not jobs:
        print("\n⚠ No jobs found in this cycle")
        logging.info("No jobs found in this scraping cycle")
        return
    
    # Load applied jobs for deduplication
    print("\nLoading application history for deduplication...")
    try:
        df_applied = pd.read_csv(CSV_FILE)
        applied_emails = set(df_applied['email'].str.lower())
        applied_job_ids = set(df_applied['job_id'])
    except:
        applied_emails = set()
        applied_job_ids = set()
    
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
    # Send applications (sequential)
    # ============================================================
    print("📧 Sending applications...\n")
    
    for job in filtered_jobs:
        if get_todays_application_count() >= MAX_APPLICATIONS_PER_DAY:
            print(f"\n⚠ Daily limit reached during cycle ({MAX_APPLICATIONS_PER_DAY})")
            print(f"Will resume at next scheduled time or reset at EOD.")
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
    
    stats = get_application_stats()
    print(f"\nOverall Statistics (All Time):")
    print(f"  Total applications: {stats['total']}")
    print(f"  Successfully sent: {stats['sent']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Unique emails contacted: {stats['unique_emails']}")
    print(f"{'='*70}\n")
    
    logging.info(f"Cycle complete: {total_applied} sent in {scrape_time:.1f}s")

def run_once_parallel():
    """Run once with parallel scraping (for testing)."""
    print("\n🤖 Running Job Application Bot (ONCE)\n")
    process_applications_parallel()

def run_scheduled_parallel():
    """Run scheduled with parallel scraping."""
    print("\n🤖 Job Application Bot Started (SCHEDULED MODE)\n")
    print("Running every 30 minutes during working hours (9 AM - 10 PM PST)")
    print("CSV will be deleted at EOD (10 PM PST)\n")
    schedule_bot(process_applications_parallel)

def show_schedule_status():
    """Display current scheduling status."""
    now_pst = get_current_pst_time()
    
    print("\n" + "="*70)
    print("SCHEDULING STATUS")
    print("="*70)
    print(f"Scheduling Enabled: {'YES' if SCHEDULING_ENABLED else 'NO'}")
    print(f"Current Time (PST): {now_pst.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Within Working Hours: {'YES' if is_within_working_hours() else 'NO'}")
    print(f"Should Run Now: {'YES' if should_run_now() else 'NO'}")
    print(f"Is EOD: {'YES (CSV will be deleted)' if is_eod() else 'NO'}")
    print(f"EOD Time: {EOD_HOUR}:{EOD_MINUTE:02d} PST")
    print("="*70 + "\n")

if __name__ == "__main__":
    # ============================================================
    # CHOOSE YOUR MODE
    # ============================================================
    
    # MODE 1: RUN ONCE (for testing)
    # run_once_parallel()
    
    # MODE 2: RUN SCHEDULED (RECOMMENDED FOR PRODUCTION)
    print("\n🚀 Starting Job Application Bot in SCHEDULED MODE")
    print("   Runs every 30 minutes during 9 AM - 10 PM PST")
    print("   CSV resets at 10 PM PST daily\n")
    
    use_preset_business_hours()
    run_scheduled_parallel()
    
    # MODE 3: SHOW STATUS FIRST
    # show_schedule_status()
    # if should_run_now():
    #     print("✓ Running now...\n")
    #     process_applications_parallel()
    # else:
    #     print("⊘ Not running - outside working hours")
