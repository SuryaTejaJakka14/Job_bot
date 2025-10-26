import yagmail
import logging
import os
from config import (
    SENDER_EMAIL, 
    SENDER_PASSWORD, 
    RESUME_PATH, 
    EMAIL_SUBJECT, 
    EMAIL_BODY,
    DRY_RUN
)

# Set up logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_application(job_title, company, recipient_email):
    """
    Send application email with resume attachment.
    
    Args:
        job_title (str): Title of the job position
        company (str): Name of the company
        recipient_email (str): Email address to send to
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    
    # Check if resume exists
    if not os.path.exists(RESUME_PATH):
        logging.error(f"Resume not found at: {RESUME_PATH}")
        print(f"✗ Error: Resume not found at {RESUME_PATH}")
        return False
    
    try:
        # Prepare email content
        subject = EMAIL_SUBJECT.format(job_title=job_title)
        body = EMAIL_BODY.format(job_title=job_title, company=company)
        
        if DRY_RUN:
            # Dry run mode - don't actually send email
            print(f"\n{'='*70}")
            print("[DRY RUN MODE - Email NOT Actually Sent]")
            print(f"{'='*70}")
            print(f"To: {recipient_email}")
            print(f"Subject: {subject}")
            print(f"Body:\n{body[:200]}...")
            print(f"Attachment: {os.path.basename(RESUME_PATH)}")
            print(f"{'='*70}\n")
            
            logging.info(f"[DRY RUN] Would send to {recipient_email} for {job_title} at {company}")
            return True
        
        # Actually send the email
        yag = yagmail.SMTP(SENDER_EMAIL, SENDER_PASSWORD)
        
        yag.send(
            to=recipient_email,
            subject=subject,
            contents=body,
            attachments=[RESUME_PATH]
        )
        
        logging.info(f"✓ Application sent to {recipient_email} for {job_title} at {company}")
        print(f"✓ Email sent successfully to {recipient_email}")
        
        return True
    
    except Exception as e:
        logging.error(f"✗ Email failed for {job_title} at {company}: {str(e)}")
        print(f"✗ Failed to send email to {recipient_email}: {str(e)}")
        return False

def test_email():
    """Test email sending (in dry run mode)."""
    print("\nTesting email sender...")
    
    success = send_application(
        job_title="Senior Java Developer",
        company="Test Company Inc.",
        recipient_email="test@example.com"
    )
    
    if success:
        print("\n✓ Email test passed!")
    else:
        print("\n✗ Email test failed!")

# Test function
if __name__ == "__main__":
    test_email()
