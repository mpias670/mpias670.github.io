import requests
from bs4 import BeautifulSoup
import json
import re
from config import CSS_SELECTORS, RESORT_DICT, RESORT_NAME_LIST

def handle_error(resort_key, error_type, message, resort_dict):
    """Handles errors by logging them and updating the resort dictionary.

    Args:
        resort_key (str): The key of the resort in the dictionary.
        error_type (str): The type of error encountered.
        message (str): A detailed error message.
        resort_dict (dict): The dictionary to update with error information.
    """
    if 'errors' not in resort_dict[resort_key]:
        resort_dict[resort_key]['errors'] = []
    resort_dict[resort_key]['errors'].append({
        'error_type': error_type,
        'message': message
    })
    print(f"Error in {resort_key}: {message}")

def request_handler(request, url):
    """_summary_

    Args:
        request (_type_): _description_
        url (_type_): _description_

    Returns:
        _type_: _description_
    """
    try: #try the primary us cert chain
        response = requests.get(url, verify=r"C:\Users\320256831\Documents\Proj\snow_api\src\consolidate.pem")


    except: 
        try: #try the uk primary cert chain
            response = requests.get(url, verify=r"C:\Users\320256831\Documents\Proj\snow_api\src\consolidateuk.pem")
            
        except: 
            try: #try the uk secondary cert chain
                response = requests.get(url, verify=r"C:\Users\320256831\Documents\Proj\snow_api\src\consolidateuk2.pem")

            except:
                response = requests.get(url)
                cert_used = response
                print('last case')
            else:
                cert_used = "secondary UK chain"


        else:
            cert_used = "primary UK chain"

    else:
        cert_used = "Normal"

    if response.status_code != 200:
        return None
    return response, cert_used

def validate_element(element_text, pattern):
    """Validates the element text against a given pattern.

    Args:
        element_text (str): The text of the extracted element.
        pattern (str): The regex pattern to validate against.

    Returns:
        bool: True if the element matches the pattern, False otherwise.
    """
    return re.match(pattern, element_text) is not None

def css_element_extractor(response, csscontainer, resort_key, resort_dict, expected_pattern=None):
    """Given a CSS Element containment, extracts the element from the provided response.

    Args:
        response (<Response> from Requests): HTTP response returned by requests.get()
        csscontainer (String): The CSS selector element corresponding with the element
        resort_key (str): The key of the resort in the dictionary.
        resort_dict (dict): The dictionary to update with element information.
        expected_pattern (str): The regex pattern that the element is expected to match.

    Returns:
        element: The extracted CSS element or a default value if the element is not present.
    """
    # handles the case where input HTTP response is empty 
    if response is None or response.status_code != 200:
        handle_error(resort_key, "HTTP Error", "Failed to fetch the webpage", resort_dict)
        return "No Data"
    
    #extract element from input HTTP reponse
    soup = BeautifulSoup(response.text, 'html.parser')
    element = soup.select_one(csscontainer)
    
    #handles the case where element is not present (maybe bc of page change?)
    if element is None:
        handle_error(resort_key, "CSS Selector Error", f"Element with selector '{csscontainer}' not found", resort_dict)
        return "No Data"
    
    element_text = element.get_text(strip=True)
    
    #handles the case where element does not match it's pattern
    if expected_pattern and not validate_element(element_text, expected_pattern):
        handle_error(resort_key, "Pattern Mismatch Error", f"Element '{element_text}' does not match expected pattern '{expected_pattern}'", resort_dict)
        return "No Data"
    
    return element_text

def fetch_resort_info(resort_key, resort_dict):
    """For a given resort name (from RESORT_DICT.keys), extract all info from the resort skireport page.

    Args:
        resort_key (_type_): The key of the resort in the dictionary.
    
    Returns:
        dict: The updated resort dictionary with extracted information.
    """
    response,cert_used = request_handler(None, RESORT_DICT[resort_key]['url'])

    if resort_dict[resort_key]['open_status']:
        #fetch all of the info 
        for selector in CSS_SELECTORS:
            pattern = CSS_SELECTORS[selector].get('pattern', None)  # Fetch the expected pattern from CSS_SELECTORS
            element = css_element_extractor(response, CSS_SELECTORS[selector]['selector'], resort_key, resort_dict, expected_pattern=pattern)
            resort_dict[resort_key][selector] = element

    return resort_dict

def fetch_resort_open_status(resort_key, resort_dict):
    """Fetches the open status of the resort.

    Args:
        resort_key (_type_): The key of the resort in the dictionary.

    Returns:
        tuple: The open status and the updated resort dictionary.
    """
    response,cert_used = request_handler(None, RESORT_DICT[resort_key]['url'])
    #if open, returns True. Otherwise, False
    open_status = css_element_extractor(response, CSS_SELECTORS['open_status']['selector'], resort_key, resort_dict)
    open_status = (open_status == "Open")
    resort_dict[resort_key]['open_status'] = open_status

    return open_status, resort_dict

def dynamic_extractor(soup, search_identifier_text, search_tag='div', sibling_tag='span', sibling_direction='next'):
    """
    Dynamically extracts an element based on the text of a nearby identifier.
    
    Args:
        soup (BeautifulSoup): Parsed HTML content.
        search_identifier_text (str): The text that identifies the .
        search_tag (str): The HTML tag of the element containing the identifier text.
        sibling_tag (str): The HTML tag of the element that contains the desired info
    
    Returns:
        str: The text content of the identified element.
    """
    identifier = soup.find(search_tag, text=search_identifier_text)
    if identifier:
        # Assuming the desired element is a sibling or in the same parent container
        target = identifier.find_next(sibling_tag).text
        if target:
            return target
    return None

def create_resort_dict(resort_dict):

    for resort in resort_dict:
        open_status, resort_dict = fetch_resort_open_status(resort, resort_dict)
        if open_status:
            resort_dict = fetch_resort_info(resort, resort_dict)
    
    return resort_dict

# Example usage
#if __name__ == "__main__":


    # resort_dict = RESORT_DICT
    # updated_resort_dict = create_resort_dict(resort_dict)

    #print(json.dumps(updated_resort_dict, indent=2))