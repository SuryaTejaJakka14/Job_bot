"""
Utility script to analyze duplicate emails in your application history.
Run this anytime to see duplicate email statistics.
"""

import pandas as pd
from database import display_email_duplicates, get_contacted_emails, get_applications_to_email

def analyze_email_patterns():
    """Analyze email contact patterns."""
    
    print("\n" + "="*70)
    print("EMAIL CONTACT PATTERN ANALYSIS")
    print("="*70 + "\n")
    
    try:
        df = pd.read_csv('applied_jobs.csv')
    except FileNotFoundError:
        print("No application history found yet.")
        return
    
    if len(df) == 0:
        print("No applications recorded.")
        return
    
    # Get all contacted emails
    contacted_emails = get_contacted_emails()
    
    print(f"Total unique emails contacted: {len(contacted_emails)}\n")
    
    # Show sample
    print("Sample contacted emails:")
    for email in contacted_emails[:10]:
        applications = get_applications_to_email(email)
        if len(applications) > 1:
            print(f"\n  {email} ({len(applications)} applications)")
            for app in applications:
                print(f"    • {app['job_title']}")
        else:
            print(f"\n  {email} (1 application)")
            print(f"    • {applications[0]['job_title']}")
    
    print(f"\n{'='*70}\n")

def generate_csv_report():
    """Generate a CSV report of all emails and their application counts."""
    
    try:
        df = pd.read_csv('applied_jobs.csv')
    except FileNotFoundError:
        print("No application history found.")
        return
    
    if len(df) == 0:
        return
    
    # Count applications per email
    email_stats = df.groupby('email').agg({
        'job_id': 'count',
        'company': lambda x: ', '.join(x.unique()),
        'applied_date': ['min', 'max']
    }).round(0)
    
    email_stats.columns = ['application_count', 'companies', 'first_applied', 'last_applied']
    email_stats = email_stats.sort_values('application_count', ascending=False)
    
    # Save to CSV
    email_stats.to_csv('email_contact_report.csv')
    
    print("\n✓ Report saved to: email_contact_report.csv\n")
    print(email_stats.head(20))

if __name__ == "__main__":
    # Display email duplicates
    display_email_duplicates()
    
    # Analyze patterns
    analyze_email_patterns()
    
    # Generate report
    generate_csv_report()
