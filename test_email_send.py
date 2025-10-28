"""
Test script to send a real email to yourself.
"""

from email_sender import send_application
from config import SENDER_EMAIL, DRY_RUN

print(f"\n{'='*70}")
print("EMAIL SENDING TEST")
print(f"{'='*70}")
print(f"\nCurrent Settings:")
print(f"  Sender Email: {SENDER_EMAIL}")
print(f"  DRY RUN Mode: {DRY_RUN}")
print(f"  Mode: {'TESTING (to yourself)' if DRY_RUN else 'LIVE (to real email)'}")

if DRY_RUN:
    print(f"\n⚠️  DRY RUN MODE IS ENABLED")
    print(f"   No actual emails will be sent")
    print(f"   Change DRY_RUN = False in config.py to send real emails\n")
else:
    print(f"\n✅ LIVE MODE - Real emails WILL be sent\n")

# Test sending
test_job = {
    'title': 'Senior Java Developer',
    'company': 'Test Company',
    'email': SENDER_EMAIL  # Send to yourself first!
}

print(f"Sending test email to: {test_job['email']}")
print(f"Job: {test_job['title']} at {test_job['company']}\n")

success = send_application(
    test_job['title'],
    test_job['company'],
    test_job['email']
)

if success:
    print(f"\n✅ Email sent successfully!")
    print(f"Check your inbox: {test_job['email']}")
else:
    print(f"\n❌ Email failed to send")
    print(f"Check logs/app.log for details")

print(f"\n{'='*70}\n")
