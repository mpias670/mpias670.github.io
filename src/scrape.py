import requests
from bs4 import BeautifulSoup
import json
from config import CSS_SELECTORS, RESORT_DICT

resort_data={}

def handler(request, url):
    response = requests.get(url, verify=False)
    
    if response.status_code != 200:
        return response
        
        # {
        #     "statusCode": response.status_code,
        #     "body": json.dumps({"error": "Failed to fetch the webpage"})
        # }
    else:
        return response
    
def css_element_extractor(response, csscontainer):
    """Given a CSS Element containment, extracts the element from the provided response

    Args:
        response (<Response> from Requests): HTTP response returned by requests.get()
        csscontainer (String): The CSS selector element corresponding with the element

    Returns:
        element: The extracted CSS element
    """
    # handling a non-successful HTTP request
    if response.status_code != 200:
        element = None
    else:
        # TODO: Add handling for checking if element fits pattern (e.g. fits x/y open) - also maybe a global error handling system where a flag is raised and reported in the json indicating an unexpected element (what is it and what was expected)
        soup = BeautifulSoup(response.text, 'html.parser')
        element = soup.select_one(csscontainer)
    return element


def fetch_resort_info(resort_key, resort_dict):
    """CALL ONLY IF RESORT IS OPEN - For a given resort name (from RESORT_DICT.keys), extract all info from the resort skireport page

    Args:
        resort_key (_type_): _description_
    
    Returns:
        element: The extracted CSS element
    """

    response = handler(None, RESORT_DICT[resort_key]['url'])

    # ONLY IF RESORT IS OPEN -> iterate through all selectors corresponding with all resort info 
    if resort_dict['open_status']:
        for selector in CSS_SELECTORS:
            element = css_element_extractor(response, CSS_SELECTORS[selector])
            resort_dict[selector] = element.get_text(strip=True)
    
    # TODO 2: add handling for elements returned with non-present handling or unexpected value
    # TODO 3: add transformations for data (e.g "7/11 open -> 7/11") from config file 
    return resort_dict

def fetch_resort_open_status(resort_key, resort_dict):
    """_summary_

    Args:
        resort_key (_type_): _description_

    Returns:
        _type_: _description_
    """

    response = handler(None, RESORT_DICT[resort_key]['url'])
    open_status = (css_element_extractor(response,CSS_SELECTORS['open_status'])=="Open")
    resort_dict['open_status'] = open_status

    return open_status, resort_dict

def create_resort_dict():
    resort_dict = RESORT_DICT

    for resort in resort_dict:
        open_status, resort_dict = fetch_resort_open_status(resort, resort_dict)
        if open_status:
            fetch_resort_info(resort,resort_dict)



# for resort_url in RESORT_URL_LIST:
#     css_element_extractor(handler(None, resort_url), CSS_SELECTORS['open_status'])

    # Example of extracting specific data
    # data = {}
    # # Extract titles
    # titles = soup.find_all('h2')
    # data['titles'] = [title.get_text() for title in titles]
    
    # Extract paragraphs
    # paragraphs = soup.find_all('p')
    # data['paragraphs'] = [para.get_text() for para in paragraphs]

    # return {
    #     "statusCode": 200,
    #     "headers": {
    #         "Content-Type": "application/json"
    #     },
    #     "body": json.dumps(data)
    # }

if __name__ == "__main__":
    #print(handler(None,r'https://www.onthesnow.com/australia/mt-buller/skireport'))  # For testing locally
    response = handler(None,r'https://www.onthesnow.com/australia/mt-buller/skireport')
    element = css_element_extractor(response, '#__next > div.container-xl.content-container > div.styles_layout__2aTIJ.layout-container > div > div.skireport_reportContent__3-14w > section:nth-child(4) > div.styles_metric__2e7Y0')''