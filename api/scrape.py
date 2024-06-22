import requests
from bs4 import BeautifulSoup
import json

def handler(request):
    url = 'https://www.onthesnow.com/ikon-pass/skireport'  # Replace with the actual URL
    response = requests.get(url)
    
    if response.status_code != 200:
        return {
            "statusCode": response.status_code,
            "body": json.dumps({"error": "Failed to fetch the webpage"})
        }
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Example of extracting specific data
    data = {}
    # Extract titles
    titles = soup.find_all('h2')
    data['titles'] = [title.get_text() for title in titles]
    
    # Extract paragraphs
    paragraphs = soup.find_all('p')
    data['paragraphs'] = [para.get_text() for para in paragraphs]
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(data)
    }

if __name__ == "__main__":
    print(handler(None))  # For testing locally
