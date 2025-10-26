import pandas as pd
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

CSV_FILE = 'applied_jobs.csv'

def initialize_database():
    """Create the CSV file if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            'job_id',
            'job_title',
            'company',
            'email',
            'applied_date',
            'status'
        ])
        df.to_csv(CSV_FILE, index=False)
        logging.info("Database initialized: applied_jobs.csv created")
        print("✓ Database initialized")
    else:
        logging.info("Database already exists")
        print("✓ Database loaded")

def is_already_applied(job_id):
    """Check if we've already applied to this job."""
    if not os.path.exists(CSV_FILE):
        return False
    
    df = pd.read_csv(CSV_FILE)
    result = job_id in df['job_id'].values
    
    if result:
        logging.info(f"Job {job_id} already applied - skipping")
    
    return result

def record_application(job_id, job_title, company, email, status='sent'):
    """Record a job application in the database."""
    df = pd.read_csv(CSV_FILE)
    
    new_row = {
        'job_id': job_id,
        'job_title': job_title,
        'company': company,
        'email': email,
        'applied_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': status
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    
    logging.info(f"Recorded application: {job_title} at {company} ({status})")
    print(f"✓ Recorded: {job_title} at {company}")

def get_application_stats():
    """Get statistics about applications."""
    if not os.path.exists(CSV_FILE):
        return {"total": 0, "sent": 0, "failed": 0}
    
    df = pd.read_csv(CSV_FILE)
    
    stats = {
        "total": len(df),
        "sent": len(df[df['status'] == 'sent']),
        "failed": len(df[df['status'] == 'failed'])
    }
    
    return stats

def get_todays_application_count():
    """Get number of applications sent today."""
    if not os.path.exists(CSV_FILE):
        return 0
    
    df = pd.read_csv(CSV_FILE)
    df['applied_date'] = pd.to_datetime(df['applied_date'])
    
    today = datetime.now().date()
    today_apps = df[df['applied_date'].dt.date == today]
    
    return len(today_apps)

# Test function
if __name__ == "__main__":
    initialize_database()
    print(f"Application stats: {get_application_stats()}")
