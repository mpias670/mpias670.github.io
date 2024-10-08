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
    """Validates the element text against a given pattern. Makes sure the extracted element is what you expect

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
def dynamic_extractor(resort_key, resort_dict, response, search_identifier_text, search_tag='div', sibling_tag='span', sibling_direction='next', deg_of_sep=1, expected_pattern=None, is_table=False, table_row=2, target_column_text='24h'):
    """
    Dynamically extracts an element based on the text of a nearby identifier, or delegates to table_extractor if `is_table` is True.
    
    Args:
        resort_key (str): The key of the resort in the dictionary.
        resort_dict (dict): The dictionary to update with element information.
        response (<Response> from Requests): HTTP response returned by requests.get()
        search_identifier_text (str): The text that identifies the element you're searching with (e.g. a table title or element identifier).
        search_tag (str): The HTML tag of the element containing the identifier text.
        sibling_tag (str): The HTML tag of the element that contains the desired info.
        sibling_direction (str): Either 'next' or 'previous' - the direction to search from the search_tag.
        deg_of_sep (int): Number of tags away the desired info is contained in.
        expected_pattern (str, optional): A regex pattern to validate the extracted data.
        is_table (bool): Whether the target element is inside a table. If True, table_extractor is called.
        table_row (int): The row index in the table to extract from (default: 2).
        target_column_text (str): The text in the first table row to find the target column (default: '24h').
    
    Returns:
        str: The text content of the identified element.
    """
    
    # Handle the case where the input HTTP response is empty or invalid
    if response is None or response.status_code != 200:
        handle_error(resort_key, "HTTP Error", "Failed to fetch the webpage", resort_dict)
        return "No Data"
    
    # Parse the HTML response
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the identifier element (like "Recent Snowfall")
    identifier = soup.find(search_tag, text=search_identifier_text)
    if not identifier:
        handle_error(resort_key, "Identifier Not Found", f"Could not find the identifier '{search_identifier_text}'", resort_dict)
        return "No Data"
    
    # If `is_table` is True, delegate to the table_extractor
    if is_table:
        return table_extractor(resort_key, resort_dict, identifier, table_row, target_column_text, expected_pattern)
    
    # Non-table logic: Find the sibling element in the specified direction and degree of separation
    if sibling_direction == 'next':
        target = identifier
        for _ in range(deg_of_sep):
            target = target.find_next(sibling_tag)
        target_text = target.text.strip() if target else None
    elif sibling_direction == 'previous':
        target = identifier
        for _ in range(deg_of_sep):
            target = target.find_previous(sibling_tag)
        target_text = target.text.strip() if target else None
    
    # Handle the case where the element does not match its expected pattern
    if expected_pattern and not validate_element(target_text, expected_pattern):
        handle_error(resort_key, "Pattern Mismatch Error", f"Element '{target_text}' does not match expected pattern '{expected_pattern}'", resort_dict)
        return "No Data"
    
    # Return the target content
    return target_text if target_text else "No Data"


def table_extractor(resort_key, resort_dict, identifier, table_row, target_column_text, expected_pattern=None):
    """
    Extracts data from a table based on the provided identifier element, column text, and row index.
    
    Args:
        resort_key (str): The key of the resort in the dictionary.
        resort_dict (dict): The dictionary to update with element information.
        identifier (BeautifulSoup element): The identifier element that precedes the table.
        table_row (int): The row index in the table to extract from (default: 2).
        target_column_text (str): The text in the first table row to find the target column (default: '24h').
        expected_pattern (str, optional): A regex pattern to validate the extracted data.
    
    Returns:
        str: The extracted value from the table.
    """
    
    # Locate the table just after the identified element
    table = identifier.find_next('table')
    if not table:
        handle_error(resort_key, "Table Not Found", "Could not find the table associated with the identifier", resort_dict)
        return "No Data"
    
    # Find all rows in the table
    rows = table.find_all('tr')
    if len(rows) < 2:
        handle_error(resort_key, "Table Structure Error", "Table does not have enough rows", resort_dict)
        return "No Data"
    
    # Find the first row (the header row) that contains day names or '24h'
    header_row = rows[0]
    headers = header_row.find_all('td')
    
    # Find the position of the column that matches `target_column_text`
    target_col_index = None
    for idx, header in enumerate(headers):
        if target_column_text in header.text.strip():
            target_col_index = idx
            break
    
    if target_col_index is None:
        handle_error(resort_key, "Column Not Found", f"Could not find the column with text '{target_column_text}'", resort_dict)
        return "No Data"
    
    # Find the target value in the corresponding position in the specified row
    target_row = rows[table_row - 1]  # Adjust for 1-based index
    target_cells = target_row.find_all('td')
    
    if target_col_index >= len(target_cells):
        handle_error(resort_key, "Column Index Error", f"Column index {target_col_index} is out of range in the target row", resort_dict)
        return "No Data"
    
    # Extract the text from the target cell
    target_value = target_cells[target_col_index].text.strip()
    
    # Validate the pattern if necessary
    if expected_pattern and not validate_element(target_value, expected_pattern):
        handle_error(resort_key, "Pattern Mismatch Error", f"Element '{target_value}' does not match expected pattern '{expected_pattern}'", resort_dict)
        return "No Data"
    
    return target_value


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
            if selector['selection_method'] == 'static':
                element = css_element_extractor(response, CSS_SELECTORS[selector]['selector'], 
                                                resort_key, resort_dict, expected_pattern=pattern)
            elif selector['selection_method'] == 'dynamic':
                element = dynamic_extractor(response, selector['identifier_text'], resort_key, 
                                            resort_dict, selector['search_tag'],selector['sibling_tag'], selector['direction'])
            
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