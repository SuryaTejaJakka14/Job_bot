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
    """
    Check if we've already applied to this specific job ID.
    
    Args:
        job_id (str): Unique job ID
        
    Returns:
        bool: True if already applied to this job
    """
    if not os.path.exists(CSV_FILE):
        return False
    
    df = pd.read_csv(CSV_FILE)
    result = job_id in df['job_id'].values
    
    if result:
        logging.info(f"Job ID {job_id} already applied - skipping")
    
    return result

def is_email_already_contacted(email):
    """
    Check if we've already sent an email to this address.
    
    This prevents sending to the same email even if it's a different job.
    
    Args:
        email (str): Email address to check
        
    Returns:
        bool: True if email has already been contacted
    """
    if not os.path.exists(CSV_FILE):
        return False
    
    if not email:
        return False
    
    df = pd.read_csv(CSV_FILE)
    
    # Check if email exists in the database
    result = email.lower() in df['email'].str.lower().values
    
    if result:
        # Find how many times this email was contacted
        email_count = len(df[df['email'].str.lower() == email.lower()])
        logging.info(f"Email {email} already contacted {email_count} time(s) - skipping")
        print(f"   ⊘ Email already contacted ({email_count} application(s) sent before)")
    
    return result

def record_application(job_id, job_title, company, email, status='sent'):
    """
    Record a job application in the database.
    
    Args:
        job_id (str): Unique job ID
        job_title (str): Job title
        company (str): Company name
        email (str): Contact email
        status (str): Application status ('sent', 'failed')
    """
    df = pd.read_csv(CSV_FILE)
    
    new_row = {
        'job_id': job_id,
        'job_title': job_title,
        'company': company,
        'email': email.lower(),  # Store email in lowercase for consistency
        'applied_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': status
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    
    logging.info(f"Recorded application: {job_title} at {company} to {email} ({status})")
    print(f"✓ Recorded: {job_title} at {company}")

def get_application_stats():
    """
    Get statistics about applications.
    
    Returns:
        dict: Statistics including total, sent, failed counts
    """
    if not os.path.exists(CSV_FILE):
        return {"total": 0, "sent": 0, "failed": 0}
    
    df = pd.read_csv(CSV_FILE)
    
    stats = {
        "total": len(df),
        "sent": len(df[df['status'] == 'sent']),
        "failed": len(df[df['status'] == 'failed']),
        "unique_emails": df['email'].nunique()
    }
    
    return stats

def get_todays_application_count():
    """
    Get number of applications sent today.
    
    Returns:
        int: Count of applications sent today
    """
    if not os.path.exists(CSV_FILE):
        return 0
    
    df = pd.read_csv(CSV_FILE)
    df['applied_date'] = pd.to_datetime(df['applied_date'])
    
    today = datetime.now().date()
    today_apps = df[df['applied_date'].dt.date == today]
    
    return len(today_apps)

def get_contacted_emails():
    """
    Get list of all contacted email addresses.
    
    Returns:
        list: List of unique email addresses already contacted
    """
    if not os.path.exists(CSV_FILE):
        return []
    
    df = pd.read_csv(CSV_FILE)
    return df['email'].unique().tolist()

def get_applications_to_email(email):
    """
    Get all applications sent to a specific email address.
    
    Args:
        email (str): Email address
        
    Returns:
        list: List of jobs applied to at this email
    """
    if not os.path.exists(CSV_FILE):
        return []
    
    df = pd.read_csv(CSV_FILE)
    jobs = df[df['email'].str.lower() == email.lower()]
    
    return jobs.to_dict('records')

def display_email_duplicates():
    """
    Display all emails that received multiple applications.
    Shows duplicate email analytics.
    """
    if not os.path.exists(CSV_FILE):
        print("No applications recorded yet")
        return
    
    df = pd.read_csv(CSV_FILE)
    
    # Count applications per email
    email_counts = df['email'].value_counts()
    
    # Find emails with more than 1 application
    duplicates = email_counts[email_counts > 1]
    
    print("\n" + "="*70)
    print("EMAIL DUPLICATE ANALYSIS")
    print("="*70)
    
    if len(duplicates) == 0:
        print("✓ No duplicate emails found!")
        print(f"Total applications: {len(df)}")
        print(f"Unique emails: {df['email'].nunique()}")
    else:
        print(f"\n⚠ Found {len(duplicates)} emails with multiple applications:\n")
        
        for email, count in duplicates.items():
            print(f"\n{email} - {count} applications sent")
            print("-" * 70)
            
            # Show all jobs sent to this email
            jobs_to_email = df[df['email'].str.lower() == email.lower()]
            for idx, (_, job) in enumerate(jobs_to_email.iterrows(), 1):
                print(f"  {idx}. {job['applied_date']}: {job['job_title']} at {job['company']}")
        
        print(f"\n{'='*70}")
        print(f"Total applications sent: {len(df)}")
        print(f"Total unique emails: {df['email'].nunique()}")
        print(f"Total duplicate emails: {len(duplicates)}")
        print(f"Total duplicate applications: {int(email_counts.sum() - df['email'].nunique())}")
        print(f"Duplicate rate: {(len(df) - df['email'].nunique()) / len(df) * 100:.1f}%")
        print(f"{'='*70}\n")

# Test function
if __name__ == "__main__":
    initialize_database()
    
    # Display statistics
    stats = get_application_stats()
    print(f"\nApplication stats: {stats}")
    
    # Display duplicates analysis
    display_email_duplicates()
