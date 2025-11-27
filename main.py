import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json


def ignitis_scraper() -> List[Dict[str, Optional[str]]]:
    """
    Scrapes all job listings from Ignitis Group career page.
    
    Returns:
        List of dictionaries containing job information with keys:
        - title: Job title
        - location: Job location
        - work_type: Type of work (e.g., full-time)
        - salary: Salary range
        - url: Link to the job posting
        - company_tag: Company/division tag (e.g., 'eso', 'ren', 'vkj')
    """
    url = "https://ignitisgrupe.lt/karjera/darbo-skelbimai"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        jobs = []
        
        # Find all job listing links
        job_links = soup.find_all('a', href=lambda x: x and '/darbo-skelbimai/' in x and x.startswith('https://ignitisgrupe.lt/darbo-skelbimai/'))
        
        for link in job_links:
            job_data = {}
            
            # Extract URL
            job_data['url'] = link.get('href', '').strip()
            
            # Extract text content from the link
            link_text = link.get_text(separator='|', strip=True)
            parts = [part.strip() for part in link_text.split('|') if part.strip()]
            
            # Parse the parts
            if len(parts) >= 1:
                # First part usually contains company tag and title
                first_part = parts[0]
                # Extract company tag (first word in lowercase)
                words = first_part.split()
                if words:
                    # Check if first word is a company tag (lowercase, short)
                    if words[0].islower() and len(words[0]) <= 4:
                        job_data['company_tag'] = words[0]
                        job_data['title'] = ' '.join(words[1:])
                    else:
                        job_data['company_tag'] = None
                        job_data['title'] = first_part
            
            # Extract location, work type, and salary from remaining parts
            job_data['location'] = parts[1] if len(parts) > 1 else None
            job_data['work_type'] = parts[2] if len(parts) > 2 else None
            
            # Find salary (usually contains "Atlyginimas" or numbers with €)
            job_data['salary'] = None
            for part in parts[3:]:
                if 'Atlyginimas' in part or '€' in part:
                    job_data['salary'] = part.replace('Atlyginimas', '').strip()
                    break
            
            # Only add if we have at least a title and URL
            if job_data.get('title') and job_data.get('url'):
                jobs.append(job_data)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_jobs = []
        for job in jobs:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)
        
        print(f"Successfully scraped {len(unique_jobs)} job listings from Ignitis Group")
        return unique_jobs
        
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return []
    except Exception as e:
        print(f"Error parsing the webpage: {e}")
        return []


def main():
    print("Scraping Ignitis Group job listings...\n")
    jobs = ignitis_scraper()
    
    if jobs:
        print(f"\nFound {len(jobs)} jobs:\n")
        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job['title']}")
            print(f"   Company: {job.get('company_tag', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Work Type: {job.get('work_type', 'N/A')}")
            print(f"   Salary: {job.get('salary', 'N/A')}")
            print(f"   URL: {job['url']}")
            print()
        
        # Optionally save to JSON file
        with open('ignitis_jobs.json', 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)
        print(f"Jobs saved to ignitis_jobs.json")
    else:
        print("No jobs found or error occurred during scraping.")


if __name__ == "__main__":
    main()
