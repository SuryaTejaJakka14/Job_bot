import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email credentials
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
RESUME_PATH = os.getenv('RESUME_PATH')

# Validate that all required variables are present
if not SENDER_EMAIL:
    raise ValueError("SENDER_EMAIL not found. Check your .env file.")
if not SENDER_PASSWORD:
    raise ValueError("SENDER_PASSWORD not found. Check your .env file.")
if not RESUME_PATH:
    raise ValueError("RESUME_PATH not found. Check your .env file.")

# Email templates
EMAIL_SUBJECT = "Application for {job_title} Position"

EMAIL_BODY = """Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. With over 12 years of experience in software development, including expertise in full-stack Java development, enterprise architecture, and technical leadership, I am confident I would be a valuable addition to your team.

Key highlights of my background:
• 11+ years of Java full-stack development with Spring Boot, Microservices, and REST APIs
• Proven track record in building scalable enterprise applications
• Experience with cloud platforms (AWS), CI/CD pipelines, and modern DevOps practices
• Strong background in Agile methodologies and cross-functional team collaboration

Please find my resume attached for your review. I would welcome the opportunity to discuss how my skills and experience align with your team's needs.

Thank you for your consideration. I look forward to hearing from you.

Best regards,
[Your Name]
[Your Phone]
[Your Email]
"""

# Scraping configuration
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Rate limiting (seconds between actions)
DELAY_BETWEEN_SCRAPES = 2
DELAY_BETWEEN_EMAILS = 10

# Daily limits
MAX_APPLICATIONS_PER_DAY = 50

# Dry run mode (set to False when ready to send real emails)
DRY_RUN = True

# ============================================================
# JOB FILTERING CONFIGURATION
# ============================================================
# Keywords to filter relevant jobs (leave empty list [] for all jobs)
# Jobs must contain at least ONE of these keywords in the title
TARGET_KEYWORDS = [
    'java',
    'full stack',
    'full-stack',
    'fullstack',
    'workday',
    'principal engineer',
    'principal developer',
    'staff engineer',
    'architect',
    'senior developer',
    'senior engineer',
    'lead engineer',
    'lead developer',
    'technical lead',
    'tech lead',
    'backend',
    'back-end',
    'spring boot',
    'microservices',
    'aws',
    'cloud engineer',
]

# Keywords to EXCLUDE (skip jobs with these in title)
EXCLUDE_KEYWORDS = [
    'qa',
    'tester',
    'testing',
    'devops',  # Remove if you want DevOps roles
    'frontend only',
    'ui only',
    'mobile',
    'ios',
    'android',
    'intern',
    'junior',
    'entry level',
]

# Minimum years of experience to filter (set to 0 to disable)
MIN_YEARS_EXPERIENCE = 5  # Will look for "5+", "7+", "10+" etc. in job title

print("✓ Configuration loaded successfully")
print(f"  - Sender Email: {SENDER_EMAIL}")
print(f"  - Resume Path: {RESUME_PATH}")
print(f"  - Dry Run Mode: {DRY_RUN}")
print(f"  - Job Filtering: {'ENABLED' if TARGET_KEYWORDS else 'DISABLED'}")
print(f"  - Target Keywords: {len(TARGET_KEYWORDS)} keywords configured")
