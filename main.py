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


def epsog_scraper() -> List[Dict[str, Optional[str]]]:
    """
    Scrapes all job listings from EPSO-G SmartRecruiters career page.
    Visits each individual job page to extract complete information.
    
    Returns:
        List of dictionaries containing job information with keys:
        - title: Job title
        - location: Job location
        - work_type: Type of work (e.g., full-time)
        - url: Link to the job posting
        - remote_work: Whether remote work is available
        - department: Department/company
        - description: Job description snippet
    """
    url = "https://careers.smartrecruiters.com/EPSOG"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("Fetching job list page...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all job listing links on SmartRecruiters
        job_links = soup.find_all('a', href=lambda x: x and '/EPSOG/' in x and x.startswith('https://jobs.smartrecruiters.com/EPSOG/'))
        
        # Remove duplicates
        seen_urls = set()
        unique_urls = []
        for link in job_links:
            job_url = link.get('href', '').strip()
            if job_url and job_url not in seen_urls:
                seen_urls.add(job_url)
                unique_urls.append(job_url)
        
        print(f"Found {len(unique_urls)} unique job listings. Fetching details...")
        
        jobs = []
        for i, job_url in enumerate(unique_urls, 1):
            try:
                print(f"  [{i}/{len(unique_urls)}] Scraping: {job_url}")
                
                # Fetch individual job page
                job_response = requests.get(job_url, headers=headers, timeout=30)
                job_response.raise_for_status()
                job_soup = BeautifulSoup(job_response.content, 'html.parser')
                
                job_data = {'url': job_url}
                
                # Extract job title from H1 with class 'job-title'
                title_elem = job_soup.find('h1', class_='job-title')
                if title_elem:
                    job_data['title'] = title_elem.get_text(strip=True)
                else:
                    # Fallback to any H1 that has content
                    all_h1 = job_soup.find_all('h1')
                    for h1 in all_h1:
                        text = h1.get_text(strip=True)
                        if text:
                            job_data['title'] = text
                            break
                    if 'title' not in job_data:
                        job_data['title'] = None
                
                # Get the full page text to parse
                page_text = job_soup.get_text()
                
                # Initialize fields
                job_data['location'] = None
                job_data['work_type'] = None
                job_data['department'] = None
                job_data['salary'] = None
                
                # Extract work type using regex - appears right after title
                import re
                work_type_match = re.search(r'(Visa darbo diena|Dalinis darbo laikas|Full-time|Part-time)', page_text)
                if work_type_match:
                    job_data['work_type'] = work_type_match.group(1)
                
                # Extract department/job family
                dept_match = re.search(r'Darbo sritis/Job family:\s*([A-ZĄČĘĖĮŠŲŪŽ][a-ząčęėįšųūž\s]+?)(?:Bendrovės|$)', page_text)
                if dept_match:
                    job_data['department'] = dept_match.group(1).strip()
                else:
                    # Fallback pattern
                    dept_match2 = re.search(r'Job family:\s*([A-Za-z\s]+?)(?:\n|Bendrovės|$)', page_text)
                    if dept_match2:
                        job_data['department'] = dept_match2.group(1).strip()
                
                # Extract location - look for city names in Lithuanian
                # Common Lithuanian cities
                lithuanian_cities = ['Vilnius', 'Kaunas', 'Klaipėda', 'Šiauliai', 'Panevėžys', 'Alytus', 
                                   'Marijampolė', 'Mažeikiai', 'Jonava', 'Utena', 'Kėdainiai', 'Telšiai',
                                   'Tauragė', 'Ukmergė', 'Visaginas', 'Plungė', 'Kretinga', 'Palanga',
                                   'Šilutė', 'Radviliškis', 'Rokiškis', 'Biržai', 'Gargždai', 'Kupiškis',
                                   'Elektrėnai', 'Jurbarkas', 'Garliava', 'Vilkaviškis', 'Raseiniai',
                                   'Anykščiai', 'Lentvaris', 'Grigiškės', 'Prienai', 'Joniškis', 'Kelmė',
                                   'Varėna', 'Kaišiadorys', 'Pasvalys', 'Kuršėnai', 'Molėtai', 'Naujoji Akmenė',
                                   'Šakiai', 'Skuodas', 'Zarasai', 'Širvintos', 'Pakruojis', 'Ignalina']
                
                job_data['location'] = None
                for city in lithuanian_cities:
                    if city in page_text:
                        job_data['location'] = city
                        break
                
                # If not found in text, try to extract from URL
                if not job_data['location']:
                    url_city_match = re.search(r'-(vilniuje|kaune|klaipedoje|siauliuose|panevezyje|alytu|marijampoleje|mazeikiuose|jonavoje|utenoje|kedainiuose|telsiuose|taurageje|ukmerge|visagine|plungeje|kretingoje|palangoje|siluteje|radviliskyje|rokiskyje|birzuose|gargzduose|kupiskyje|elektrenuse|jurbarke|garliavoje|vilkaviskyje|raseinuose|anyksciuose|lentvaryje|grigiskese|prienuose|joniskyje|kelmeje|varenoje|kaisiadoruose|pasvalyje|kursenuose|moletuose|naujoje-akmene|sakiuose|skuode|zarasuose|sirvintose|pakruojyje|ignalina)', job_url.lower())
                    if url_city_match:
                        # Map URL form to city name
                        city_map = {
                            'vilniuje': 'Vilnius', 'kaune': 'Kaunas', 'klaipedoje': 'Klaipėda',
                            'siauliuose': 'Šiauliai', 'panevezyje': 'Panevėžys', 'marijampoleje': 'Marijampolė',
                            'telsiuose': 'Telšiai', 'rokiskyje': 'Rokiškis', 'kupiskyje': 'Kupiškis',
                            'vilkaviskyje': 'Vilkaviškis', 'pasvalyje': 'Pasvalys', 'moletuose': 'Molėtai',
                            'ignalina': 'Ignalina', 'plungeje': 'Plungė'
                        }
                        url_city = url_city_match.group(1)
                        job_data['location'] = city_map.get(url_city, url_city.capitalize())
                
                # Check for remote work
                job_data['remote_work'] = 'nuotoliniu' in page_text.lower() or 'remote' in page_text.lower()
                
                # Extract salary information
                salary_match = re.search(r'atlygis\s+(\d+[–-]\d+\s*(?:EUR|€))', page_text, re.IGNORECASE)
                if salary_match:
                    job_data['salary'] = salary_match.group(1).strip()
                
                # Extract job description sections
                descriptions = []
                for heading in ['Darbo aprašymas', 'Reikalavimai']:
                    elem = job_soup.find(string=heading)
                    if elem and elem.parent:
                        # Get the next sibling or parent's next sibling content
                        next_elem = elem.parent.find_next()
                        if next_elem:
                            desc_text = next_elem.get_text(strip=True)
                            if desc_text and len(desc_text) > 20:
                                descriptions.append(desc_text[:150])
                
                if descriptions:
                    job_data['description'] = ' | '.join(descriptions)
                else:
                    job_data['description'] = None
                
                jobs.append(job_data)
                
                # Small delay to avoid overwhelming the server
                import time
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    Error scraping {job_url}: {e}")
                continue
        
        print(f"\nSuccessfully scraped {len(jobs)} job listings from EPSO-G")
        return jobs
        
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return []
    except Exception as e:
        print(f"Error parsing the webpage: {e}")
        return []


def main():
    print("=" * 60)
    print("Scraping Ignitis Group job listings...")
    print("=" * 60 + "\n")
    
    ignitis_jobs = ignitis_scraper()
    
    if ignitis_jobs:
        print(f"\nFound {len(ignitis_jobs)} jobs:\n")
        for i, job in enumerate(ignitis_jobs, 1):
            print(f"{i}. {job['title']}")
            print(f"   Company: {job.get('company_tag', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Work Type: {job.get('work_type', 'N/A')}")
            print(f"   Salary: {job.get('salary', 'N/A')}")
            print(f"   URL: {job['url']}")
            print()
        
        with open('ignitis_jobs.json', 'w', encoding='utf-8') as f:
            json.dump(ignitis_jobs, f, ensure_ascii=False, indent=2)
        print(f"Jobs saved to ignitis_jobs.json\n")
    else:
        print("No jobs found or error occurred during scraping.\n")
    
    print("=" * 60)
    print("Scraping EPSO-G job listings...")
    print("=" * 60 + "\n")
    
    epsog_jobs = epsog_scraper()
    
    if epsog_jobs:
        print(f"\nFound {len(epsog_jobs)} jobs:\n")
        for i, job in enumerate(epsog_jobs, 1):
            print(f"{i}. {job.get('title', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Work Type: {job.get('work_type', 'N/A')}")
            print(f"   Department: {job.get('department', 'N/A')}")
            print(f"   Salary: {job.get('salary', 'N/A')}")
            print(f"   Remote Work: {'Yes' if job.get('remote_work') else 'No'}")
            print(f"   URL: {job['url']}")
            print()
        
        with open('epsog_jobs.json', 'w', encoding='utf-8') as f:
            json.dump(epsog_jobs, f, ensure_ascii=False, indent=2)
        print(f"Jobs saved to epsog_jobs.json\n")
    else:
        print("No jobs found or error occurred during scraping.\n")
    
    # Summary
    print("=" * 60)
    print("SCRAPING SUMMARY")
    print("=" * 60)
    print(f"Total Ignitis Group jobs: {len(ignitis_jobs)}")
    print(f"Total EPSO-G jobs: {len(epsog_jobs)}")
    print(f"Grand Total: {len(ignitis_jobs) + len(epsog_jobs)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
