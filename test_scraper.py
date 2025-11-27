import requests
from bs4 import BeautifulSoup

url = "https://jobs.smartrecruiters.com/EPSOG/744000095884850-inziniere-ius-pastociu-skyriuje-panevezyje-"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.content, 'html.parser')

print("=== H1 Tags ===")
h1_tags = soup.find_all('h1')
for i, h1 in enumerate(h1_tags):
    print(f"H1 #{i+1}: '{h1.get_text(strip=True)}'")
    print(f"  Has class: {h1.get('class')}")
    print()

print("\n=== Looking for title in different ways ===")
# Try meta tags
title_meta = soup.find('meta', property='og:title')
if title_meta:
    print(f"OG Title: {title_meta.get('content')}")

# Try page title
if soup.title:
    print(f"Page Title: {soup.title.get_text(strip=True)}")

print("\n=== Testing location/work type extraction ===")
lines = [line.strip() for line in soup.get_text().split('\n') if line.strip()]
for i, line in enumerate(lines[:50]):
    print(f"{i}: {line[:100]}")
    
print("\n=== Looking for specific patterns ===")
for i, line in enumerate(lines):
    if 'Lietuva' in line or 'Visa darbo diena' in line or 'Darbo sritis' in line or 'atlygis' in line.lower():
        print(f"Line {i}: {line}")
