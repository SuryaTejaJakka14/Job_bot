"""
Enhanced email sender with professional HTML formatting.
Uses custom cover letter body provided by user.
- Bold text in body is BLACK
- Signature in BLUE
- Left-aligned format
- Professional email style
"""

import yagmail
import logging
from config import SENDER_EMAIL, SENDER_PASSWORD, RESUME_PATH, DRY_RUN

# Set up logging
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_html_email(job_title, company, recipient_email):
    """
    Create a professional HTML-formatted email with custom cover letter.
    - Bold text in body is BLACK
    - Signature is BLUE
    - Left-aligned
    """
    
    # Personalization - UPDATE THESE WITH YOUR INFO
    sender_name = "Surya Teja"
    sender_phone = "(480) 580-4821"
    sender_linkedin = "www.linkedin.com/in/teja-j14"
    
    # Custom email body with formatting - ALL ON ONE LINE
    html_body = f"<html><head><style>body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; text-align: left; }} .email-content {{ max-width: 100%; padding: 0; }} p {{ margin: 12px 0; font-size: 14px; line-height: 1.6; }} .highlight {{ color: #000; font-weight: bold; }} .bullet-point {{ margin-left: 20px; margin-top: 5px; font-size: 14px; line-height: 1.5; }} .section-title {{ color: #000; font-weight: bold; margin-top: 12px; margin-bottom: 8px; font-size: 14px; }} .signature {{ margin-top: 15px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 13px; }} .signature-name {{ font-weight: bold; color: #0077b5; font-size: 15px; margin-bottom: 3px; }} .signature-detail {{ margin: 2px 0; color: #0077b5; font-size: 13px; }} .signature-link {{ color: #0077b5; text-decoration: none; }} .signature-link:hover {{ text-decoration: underline; }}</style></head><body><div class='email-content'><p>Hi, </p><p>I hope this message finds you well.</p><p>I'm reaching out to express my interest in <span class='highlight'>current or upcoming opportunities for a Principal Java Full-Stack Engineer / Technical Lead role within your client network</span>. With <span class='highlight'>over 12 years of experience</span> in enterprise-scale application development, cloud-native architecture, and full-stack engineering, I've successfully delivered large-scale modernization programs for top financial, regulatory, and public sector clients including <span class='highlight'>Wells Fargo, Moody's, and the State of Wisconsin</span>.</p><p>In my current role as a <span class='highlight'>Principal Engineer at Wells Fargo</span>, I've been leading the digital core modernization initiative — architecting a <span class='highlight'>200+ microservices platform</span> using <span class='highlight'>Java 17/21, Spring Boot 3.x, Spring Cloud 2023.x, and Apache Kafka 3.4</span> on <span class='highlight'>AWS EKS with Terraform, ArgoCD, and Istio service mesh</span>. I've established enterprise-wide standards for microservices, event-driven design, and zero-trust security, achieving a <span class='highlight'>40% cost reduction</span> while supporting <span class='highlight'>3× traffic growth</span> and maintaining <span class='highlight'>99.97%+ uptime</span> in production environments.</p><p>My expertise extends across the full software lifecycle, from architecture and API design to CI/CD automation, observability, and compliance. I'm deeply experienced in:</p><div class='bullet-point'>• <span class='highlight'>Distributed systems and event streaming:</span> Kafka, Pulsar, RabbitMQ, Flink, Iceberg</div><div class='bullet-point'>• <span class='highlight'>Front-end engineering:</span> React 18, Next.js 13, TypeScript 5.x, D3.js visualizations</div><div class='bullet-point'>• <span class='highlight'>Cloud and DevOps:</span> AWS (EKS, RDS, Lambda, S3), Terraform, ArgoCD, GitLab CI/CD, Jenkins</div><div class='bullet-point'>• <span class='highlight'>Security and compliance:</span> OAuth 2.1/FAPI, HashiCorp Vault, mTLS, SOC 2 Type II, PCI DSS</div><div class='bullet-point'>• <span class='highlight'>Data architecture:</span> PostgreSQL, Cassandra, MongoDB, Redis, Oracle, real-time analytics pipelines</div><div class='bullet-point'>• <span class='highlight'>Leadership and mentorship:</span> Building and guiding teams of 20+ engineers, architecture governance, and career development frameworks</div><p>Throughout my career, I've demonstrated the ability to translate complex business requirements into scalable, secure, and maintainable systems, particularly in <span class='highlight'>regulated financial environments</span> where performance, resilience, and auditability are paramount. My work has been instrumental in driving enterprise transformation initiatives, achieving measurable business outcomes such as:</p><div class='bullet-point'>• <span class='highlight'>Reducing deployment cycles</span> from 4 weeks to 2 days</div><div class='bullet-point'>• <span class='highlight'>Improving fraud-detection accuracy</span> by 15%</div><div class='bullet-point'>• <span class='highlight'>Automating regulatory reporting</span> from 6 weeks to 3 days</div><p>I'm passionate about technology leadership, innovation, and driving engineering excellence through architectural best practices and mentorship. I believe my blend of <span class='highlight'>deep technical expertise, domain knowledge in banking and financial services, and hands-on leadership</span> would bring significant value to your clients' strategic initiatives.</p><p>I've attached my latest resume, which provides a detailed overview of my background, achievements, and technology stack. I would appreciate the opportunity to discuss how my experience aligns with your clients' needs and explore suitable positions within your portfolio.</p><p>Thank you for considering my application. I look forward to connecting and discussing potential opportunities.</p><p>Best regards,</p><div class='signature'><div class='signature-name'>{sender_name}</div><div class='signature-detail'><span class='highlight'>Principal Engineer | Full-Stack Java Developer</span></div><div class='signature-detail'>Phone: {sender_phone}</div><div class='signature-detail'>Email: {SENDER_EMAIL}</div><div class='signature-detail'>LinkedIn: <a href='{sender_linkedin}' class='signature-link'>{sender_linkedin}</a></div><div class='signature-detail' style='margin-top: 8px; font-size: 12px; color: #888;'>Open to: Remote & Local Opportunities | Available for Immediate Engagement</div></div></div></body></html>"
    
    return html_body

def send_application(job_title, company, recipient_email):
    """
    Send a professional job application email with resume.
    
    Args:
        job_title (str): Job title
        company (str): Company name
        recipient_email (str): Recipient email address
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    
    try:
        # Email subject with job title and company
        subject = f"Experienced Principal Java Full-Stack Engineer – Available for New Opportunities"
        
        # Generate HTML email body
        html_body = create_html_email(job_title, company, recipient_email)
        
        # DRY RUN MODE: Show email preview instead of sending
        if DRY_RUN:
            print(f"\n{'='*70}")
            print(f"[DRY RUN MODE - Email NOT Actually Sent]")
            print(f"{'='*70}")
            print(f"To: {recipient_email}")
            print(f"Subject: {subject}")
            print(f"\nEmail Preview:")
            print(f"{'-'*70}")
            print(f"Hi,")
            print(f"\nI hope this message finds you well.")
            print(f"\nI'm reaching out to express my interest in current or upcoming")
            print(f"opportunities for a {job_title} role within your client network.")
            print(f"With over 12 years of experience in enterprise-scale application")
            print(f"development, cloud-native architecture, and full-stack engineering,")
            print(f"I've successfully delivered large-scale modernization programs for")
            print(f"top financial, regulatory, and public sector clients including")
            print(f"Wells Fargo, Moody's, and the State of Wisconsin.")
            print(f"\nIn my current role as a Principal Engineer at Wells Fargo...")
            print(f"\n[Professional cover letter with achievements, expertise, and outcomes]")
            print(f"\nBest regards,")
            print(f"\nSurya Teja")
            print(f"Principal Engineer | Full-Stack Java Developer")
            print(f"📱 Phone: (480) 580-4821")
            print(f"📧 Email: {SENDER_EMAIL}")
            print(f"💼 LinkedIn: www.linkedin.com/in/teja-j14")
            print(f"\nAttachment: resume.pdf")
            print(f"{'='*70}\n")
            
            logging.info(f"[DRY RUN] Email prepared to {recipient_email} for {job_title} at {company}")
            return True
        
        # LIVE MODE: Actually send the email
        print(f"\n   Sending email to {recipient_email}...")
        
        # Create SMTP connection using yagmail
        yag = yagmail.SMTP(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Send email with HTML body and attachment
        yag.send(
            to=recipient_email,
            subject=subject,
            contents=[html_body],  # HTML body
            attachments=RESUME_PATH  # Attach resume
        )
        
        yag.close()
        
        logging.info(f"✓ Email sent successfully to {recipient_email} for {job_title} at {company}")
        print(f"   ✓ Email sent successfully!")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"✗ Failed to send email to {recipient_email}: {error_msg}")
        print(f"   ✗ Failed to send email: {error_msg}")
        return False

def test_html_email():
    """Test HTML email formatting."""
    print("\n" + "="*70)
    print("HTML EMAIL TEST")
    print("="*70 + "\n")
    
    html = create_html_email("Principal Java Full-Stack Engineer", "Client Company", "test@example.com")
    
    # Save to file for preview
    with open('email_preview.html', 'w') as f:
        f.write(html)
    
    print("✓ HTML email template created!")
    print("✓ Saved to: email_preview.html")
    print("\nYou can open this file in your browser to see the formatted email.")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_html_email()
