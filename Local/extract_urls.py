import requests
from bs4 import BeautifulSoup
import certifi
from dotenv import load_dotenv

def extract_links(url):
    # Fetch the webpage content with certifi for SSL verification
    response = requests.get(url, verify=False)
    # "C:\\Users\\320256831\\Documents\\Proj\\snow_api\\Resources\\onethesnowcert.crt")
    if response.status_code != 200:
        print(f"Failed to fetch the webpage: {response.status_code}")
        return []
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract all anchor tags
    anchor_tags = soup.find_all('a', href=True)
    
    # Extract the href attribute (links) from each anchor tag
    links = [tag['href'] for tag in anchor_tags]
    
    return links

def save_links_to_file(links, filename):
    with open(filename, 'w') as file:
        for link in links:
            file.write(f"{link}\n")

if __name__ == "__main__":
    url = 'https://www.onthesnow.com/ikon-pass/skireport'  # Replace with the actual URL you want to scrape
    links = extract_links(url)
    
    if links:
        # Save the extracted links to a file
        save_links_to_file(links, 'links.txt')
        print(f"Extracted {len(links)} links and saved to links.txt")
    else:
        print("No links found.")
