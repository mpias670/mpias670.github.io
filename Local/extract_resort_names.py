import requests
from bs4 import BeautifulSoup
from config import CSS_SELECTORS
from config import RESORT_URL_LIST
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extract_resort_name(url, css_selector):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        element = soup.select_one(css_selector)
        if element:
            return element.next
        else:
            return 'Resort name not found'
    except requests.exceptions.RequestException as e:
        return f'Error: {e}'

def main():
    css_selector = CSS_SELECTORS['resort_name']
    resort_names = []

    for url in RESORT_URL_LIST:
        resort_name = extract_resort_name(url, css_selector)
        print(resort_name)
        resort_names.append(resort_name)

    with open('resort_names.txt', 'w') as file:
        for name in resort_names:
            file.write(name + '\n')

if __name__ == '__main__':
    main()

