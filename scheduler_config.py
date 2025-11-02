"""
Scheduling configuration for job application bot.
- Schedule every 30 minutes
- Set specific time periods (working hours)
- Auto-reset CSV file after midnight
- Track daily application limits
"""

import schedule
import time
import logging
from datetime import datetime, time as dt_time
from config import DRY_RUN

# Set up logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============================================================
# SCHEDULING CONFIGURATION - CUSTOMIZE THESE SETTINGS
# ============================================================

# Enable/disable scheduling
SCHEDULING_ENABLED = True

# Schedule interval (in minutes)
SCHEDULE_INTERVAL_MINUTES = 3  # Run every 30 minutes

# Time period configuration (working hours)
# Set these to define when the bot should run
START_TIME = dt_time(7,0,0)   # 9:00 AM - When to START running
END_TIME = dt_time(15,0,0)    # 6:00 PM (18:00) - When to STOP running

# Days to run on
DAYS_TO_RUN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']  # Weekdays only
# For all days: DAYS_TO_RUN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Auto-reset CSV after midnight
AUTO_RESET_CSV_AFTER_MIDNIGHT = True

# ============================================================

def is_within_working_hours():
    """
    Check if current time is within working hours.
    
    Returns:
        bool: True if within working hours, False otherwise
    """
    current_time = datetime.now().time()
    current_day = datetime.now().strftime('%A')
    
    # Check if today is in DAYS_TO_RUN
    if current_day not in DAYS_TO_RUN:
        logging.info(f"Bot not scheduled for {current_day}. Skipping.")
        return False
    
    # Check if current time is between START_TIME and END_TIME
    if current_time < START_TIME:
        logging.info(f"Before working hours ({START_TIME}). Skipping.")
        return False
    
    if current_time > END_TIME:
        logging.info(f"After working hours ({END_TIME}). Skipping.")
        return False
    
    return True

def should_run_now():
    """
    Check if bot should run at this moment.
    - Within working hours?
    - Right day of week?
    
    Returns:
        bool: True if should run, False otherwise
    """
    if not SCHEDULING_ENABLED:
        return False
    
    if not is_within_working_hours():
        return False
    
    return True

def reset_daily_counter():
    """
    Reset the daily application counter after midnight.
    This allows the bot to send MAX_APPLICATIONS_PER_DAY again on the new day.
    """
    try:
        from database import initialize_database
        
        # This creates a fresh CSV if needed
        initialize_database()
        
        logging.info("Daily counter reset after midnight")
        print("✓ Daily counter reset - new day started!")
        
    except Exception as e:
        logging.error(f"Error resetting daily counter: {str(e)}")

def schedule_bot(process_applications_func):
    """
    Set up the scheduling for the bot.
    
    Args:
        process_applications_func: The function to call on schedule
    """
    
    print("\n" + "="*70)
    print("SCHEDULING CONFIGURATION")
    print("="*70)
    print(f"Status: {'ENABLED' if SCHEDULING_ENABLED else 'DISABLED'}")
    print(f"Interval: Every {SCHEDULE_INTERVAL_MINUTES} minutes")
    print(f"Working Hours: {START_TIME.strftime('%H:%M')} - {END_TIME.strftime('%H:%M')}")
    print(f"Days: {', '.join(DAYS_TO_RUN)}")
    print(f"Auto-reset CSV: {'YES' if AUTO_RESET_CSV_AFTER_MIDNIGHT else 'NO'}")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print("="*70 + "\n")
    
    if not SCHEDULING_ENABLED:
        print("⚠ Scheduling is DISABLED in config. Enable to use scheduling.")
        return
    
    # Create wrapper function that checks working hours
    def scheduled_job():
        if should_run_now():
            print(f"\n🤖 [START] Running cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            process_applications_func()
            print(f"✓ [END] Cycle completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        else:
            print(f"⊘ Outside working hours - skipping cycle at {datetime.now().strftime('%H:%M:%S')}")
    
    # Schedule every X minutes
    schedule.every(SCHEDULE_INTERVAL_MINUTES).minutes.do(scheduled_job)
    
    # Schedule daily reset at midnight (00:00)
    if AUTO_RESET_CSV_AFTER_MIDNIGHT:
        schedule.every().day.at("00:00").do(reset_daily_counter)
    
    print(f"✓ Scheduler configured")
    print(f"  - Will run every {SCHEDULE_INTERVAL_MINUTES} minutes")
    print(f"  - Only between {START_TIME.strftime('%H:%M')} - {END_TIME.strftime('%H:%M')}")
    print(f"  - Only on: {', '.join(DAYS_TO_RUN)}")
    print(f"  - Daily reset at: 00:00 (midnight)")
    print(f"\n Press Ctrl+C to stop\n")
    
    # Run the scheduler
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every 60 seconds
    except KeyboardInterrupt:
        print("\n\n⏹ Bot stopped by user")
        logging.info("Bot stopped by user")

# ============================================================
# QUICK PRESET CONFIGURATIONS
# ============================================================

def use_preset_business_hours():
    """9 AM - 6 PM, Monday-Friday (default office hours)"""
    global START_TIME, END_TIME, DAYS_TO_RUN
    START_TIME = dt_time(7, 0)
    END_TIME = dt_time(23, 59)
    DAYS_TO_RUN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    print("✓ Preset: Business Hours (9 AM - 6 PM, Mon-Fri)")

def use_preset_extended_hours():
    """8 AM - 8 PM, Monday-Friday"""
    global START_TIME, END_TIME, DAYS_TO_RUN
    START_TIME = dt_time(8, 0)
    END_TIME = dt_time(22, 0)
    DAYS_TO_RUN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    print("✓ Preset: Extended Hours (8 AM - 8 PM, Mon-Fri)")

def use_preset_24_7():
    """24/7 - Every day, all day"""
    global START_TIME, END_TIME, DAYS_TO_RUN
    START_TIME = dt_time(0, 0)
    END_TIME = dt_time(23, 59)
    DAYS_TO_RUN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    print("✓ Preset: 24/7 Mode (All day, every day)")

def use_preset_night_shift():
    """6 PM - 9 AM, every day"""
    global START_TIME, END_TIME, DAYS_TO_RUN
    START_TIME = dt_time(18, 0)
    END_TIME = dt_time(9, 0)  # Note: This crosses midnight
    DAYS_TO_RUN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    print("✓ Preset: Night Shift (6 PM - 9 AM, every day)")
