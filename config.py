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
EMAIL_SUBJECT = "Experienced Principal Java Full-Stack Engineer – Available for New Opportunities"

EMAIL_BODY = """Hi, 
I hope this message finds you well.

I’m reaching out to express my interest in current or upcoming opportunities for a Principal Java Full-Stack Engineer / Technical Lead role within your client network. With over 12 years of experience in enterprise-scale application development, cloud-native architecture, and full-stack engineering, I’ve successfully delivered large-scale modernization programs for top financial, regulatory, and public sector clients including Wells Fargo, Moody’s, and the State of Wisconsin.

In my current role as a Principal Engineer at Wells Fargo, I’ve been leading the digital core modernization initiative — architecting a 200+ microservices platform using Java 17/21, Spring Boot 3.x, Spring Cloud 2023.x, and Apache Kafka 3.4 on AWS EKS with Terraform, ArgoCD, and Istio service mesh. I’ve established enterprise-wide standards for microservices, event-driven design, and zero-trust security, achieving a 40% cost reduction while supporting 3× traffic growth and maintaining 99.97%+ uptime in production environments.

My expertise extends across the full software lifecycle, from architecture and API design to CI/CD automation, observability, and compliance. I’m deeply experienced in:

Distributed systems and event streaming: Kafka, Pulsar, RabbitMQ, Flink, Iceberg

Front-end engineering: React 18, Next.js 13, TypeScript 5.x, D3.js visualizations

Cloud and DevOps: AWS (EKS, RDS, Lambda, S3), Terraform, ArgoCD, GitLab CI/CD, Jenkins

Security and compliance: OAuth 2.1/FAPI, HashiCorp Vault, mTLS, SOC 2 Type II, PCI DSS

Data architecture: PostgreSQL, Cassandra, MongoDB, Redis, Oracle, real-time analytics pipelines

Leadership and mentorship: Building and guiding teams of 20+ engineers, architecture governance, and career development frameworks

Throughout my career, I’ve demonstrated the ability to translate complex business requirements into scalable, secure, and maintainable systems, particularly in regulated financial environments where performance, resilience, and auditability are paramount. My work has been instrumental in driving enterprise transformation initiatives, achieving measurable business outcomes such as reducing deployment cycles from 4 weeks to 2 days, improving fraud-detection accuracy by 15%, and automating regulatory reporting from 6 weeks to 3 days.

I’m passionate about technology leadership, innovation, and driving engineering excellence through architectural best practices and mentorship. I believe my blend of deep technical expertise, domain knowledge in banking and financial services, and hands-on leadership would bring significant value to your clients’ strategic initiatives.

I’ve attached my latest resume, which provides a detailed overview of my background, achievements, and technology stack. I would appreciate the opportunity to discuss how my experience aligns with your clients’ needs and explore suitable positions within your portfolio.

Thank you for considering my application. I look forward to hearing from you and hopefully collaborating on potential opportunities.
"""

# Scraping configuration
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Rate limiting (seconds between actions)
DELAY_BETWEEN_SCRAPES = 2
DELAY_BETWEEN_EMAILS = 10

# Daily limits
MAX_APPLICATIONS_PER_DAY = 1000

# Dry run mode (set to False when ready to send real emails)
DRY_RUN = False

# ============================================================
# SEARCH KEYWORDS CONFIGURATION
# ============================================================
# Keywords to search on jobs.nvoids.com
# The bot will perform separate searches for each keyword
SEARCH_KEYWORDS = [
    'java'
]

# Maximum number of pages to scrape per search (each page has ~100 jobs)
MAX_PAGES_PER_SEARCH = 5

# ============================================================
# JOB FILTERING CONFIGURATION
# ============================================================
# Keywords to filter relevant jobs (leave empty list [] for all jobs)
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
    'microservices',
    'selenium',
    'cucumber',
    'rest api',
]

# Keywords to EXCLUDE (skip jobs with these in title)
EXCLUDE_KEYWORDS = [
    'ui only',
    'mobile',
    'ios',
    'android',
    'intern',
    'junior',
    'entry level',
]

# Minimum years of experience to filter (set to 0 to disable)
MIN_YEARS_EXPERIENCE = 5

# Selenium/Browser settings
HEADLESS_BROWSER = True  # Set to False to see the browser in action (for debugging)
BROWSER_WAIT_TIME = 10  # Seconds to wait for elements to load

print("✓ Configuration loaded successfully")
print(f"  - Sender Email: {SENDER_EMAIL}")
print(f"  - Resume Path: {RESUME_PATH}")
print(f"  - Dry Run Mode: {DRY_RUN}")
print(f"  - Search Keywords: {len(SEARCH_KEYWORDS)} configured")
print(f"  - Job Filtering: {'ENABLED' if TARGET_KEYWORDS else 'DISABLED'}")
# ============================================================
# PARALLEL SCRAPING CONFIGURATION
# ============================================================

# Number of parallel threads for job scraping
# Recommended: 3-5 (higher = faster but more resource usage)
# Too high: May get blocked by website or cause crashes
PARALLEL_WORKERS = 3

# Maximum threads to use
#MAX_PARALLEL_WORKERS = 5

# Use parallel scraping or sequential?
USE_PARALLEL_SCRAPING = True
