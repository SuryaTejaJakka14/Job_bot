"""
Test file to verify job filtering logic works correctly.
Run this to test your keywords before running the full scraper.
"""

from scraper import is_relevant_job, extract_years_experience
from config import TARGET_KEYWORDS, EXCLUDE_KEYWORDS, MIN_YEARS_EXPERIENCE

def test_filtering():
    """Test the job filtering with sample job titles."""
    
    print("\n" + "="*70)
    print("JOB FILTERING TEST")
    print("="*70 + "\n")
    
    print("Current Filter Configuration:")
    print(f"  Target Keywords: {TARGET_KEYWORDS}")
    print(f"  Exclude Keywords: {EXCLUDE_KEYWORDS}")
    print(f"  Minimum Years: {MIN_YEARS_EXPERIENCE}")
    print("\n" + "="*70 + "\n")
    
    # Sample job titles (mix of relevant and irrelevant)
    test_jobs = [
        # Should PASS (relevant)
        "Senior Java Developer - 8+ years experience",
        "Full Stack Engineer with Spring Boot",
        "Principal Software Engineer - Backend",
        "Java Architect - Microservices Expert",
        "Workday HCM Consultant - Remote",
        "Lead Java Developer with AWS",
        "Staff Engineer - Full Stack Development",
        
        # Should FAIL (filtered out)
        "QA Automation Engineer - 10 years",  # QA excluded
        "Junior Java Developer",  # Junior excluded
        "Frontend Developer - React Only",  # Frontend only
        "Mobile Developer - iOS/Android",  # Mobile excluded
        "Python Developer",  # No matching keyword
        "Data Analyst with SQL",  # No matching keyword
        "DevOps Engineer - Kubernetes",  # DevOps excluded (if in exclude list)
        "Java Developer - 3 years experience",  # Less than min years
    ]
    
    passed = 0
    failed = 0
    
    for job_title in test_jobs:
        years = extract_years_experience(job_title)
        result = is_relevant_job(
            job_title, 
            TARGET_KEYWORDS, 
            EXCLUDE_KEYWORDS, 
            MIN_YEARS_EXPERIENCE
        )
        
        status = "✓ PASS" if result else "✗ FAIL"
        years_text = f"({years}+ years)" if years > 0 else "(no years specified)"
        
        print(f"{status} {years_text}")
        print(f"     {job_title}")
        print()
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print("="*70)
    print(f"Results: {passed} passed, {failed} filtered out")
    print("="*70 + "\n")
    
    print("Tips:")
    print("  - If too many jobs are filtered, broaden TARGET_KEYWORDS")
    print("  - If too few are filtered, add more EXCLUDE_KEYWORDS")
    print("  - Adjust MIN_YEARS_EXPERIENCE based on your experience level")
    print()

if __name__ == "__main__":
    test_filtering()
