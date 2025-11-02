# Save as: debug_page_structure.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def debug_page():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Loading page...")
        driver.get("https://jobs.nvoids.com/search_sph.jsp")
        time.sleep(3)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Debug: Find ALL tables
        tables = soup.find_all('table')
        print(f"\n✓ Found {len(tables)} tables on the page\n")
        
        # Debug: Check first table
        if tables:
            table = tables[0]
            rows = table.find_all('tr')
            print(f"First table has {len(rows)} rows\n")
            
            # Show first 3 rows
            for row_idx, row in enumerate(rows[:3]):
                cols = row.find_all(['td', 'th'])
                print(f"Row {row_idx}: {len(cols)} columns")
                for col_idx, col in enumerate(cols):
                    text = col.get_text(strip=True)[:80]
                    print(f"  Col {col_idx}: {text}")
                print()
        
        # Debug: Find ALL links
        all_links = soup.find_all('a', href=True)
        print(f"\nTotal links on page: {len(all_links)}\n")
        
        # Show links with "job" in href
        job_links = [l for l in all_links if 'job' in l.get('href', '').lower()]
        print(f"Links containing 'job': {len(job_links)}\n")
        
        for idx, link in enumerate(job_links[:5]):
            href = link.get('href')
            text = link.get_text(strip=True)[:60]
            print(f"{idx+1}. href: {href}")
            print(f"   text: {text}\n")
        
        # Save full page source for inspection
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("\n✓ Full page source saved to: page_source.html")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_page()
