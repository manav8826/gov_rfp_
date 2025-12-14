import requests
from bs4 import BeautifulSoup

def test_live_site():
    print("Testing Real Internet Connectivity & Scraping...")
    
    # 1. Target URL (using a stable public site for demonstration)
    url = "https://gem.gov.in/cppp?utm_source=chatgpt.com" 
    print(f"Fetching: {url}")
    
    try:
        # 2. Real Network Call
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # 3. Real HTML Parsing
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title').text.strip()
            print(f"Success! Page Title Found: '{title}'")
            print("LIVE URL FETCHING IS WORKING.")
        else:
            print("Failed to fetch page.")
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_live_site()
