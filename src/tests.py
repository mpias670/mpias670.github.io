import scraper
from config import CSS_SELECTORS, RESORT_DICT, RESORT_NAME_LIST
from bs4 import BeautifulSoup

resort_dict = RESORT_DICT

def test_resort_open(resort_dict):
    
    for idx,resort_name in enumerate(RESORT_NAME_LIST):
        if idx > 51:
            print("Mountain " + resort_name + ": Number " + str(idx) + "/" + str(len(RESORT_NAME_LIST)-1))
            open_status, resort_dict_open = scraper.fetch_resort_open_status(resort_name,resort_dict)
            print(open_status)

def test_create_resort_dict(resort_dict):
    resort_dict = scraper.create_resort_dict(resort_dict)
    return resort_dict


def test_element_extract(selector_name,resort_dict):
    pattern = CSS_SELECTORS[selector_name]['pattern']
    for resort in resort_dict:
        response,cert_used = scraper.request_handler(None, resort_dict[resort]['url'])
        element = scraper.css_element_extractor(response, CSS_SELECTORS[selector_name]['selector'], resort, resort_dict, expected_pattern=pattern)
        resort_dict[resort][selector_name] = element
        resort_dict[resort]['cert_used'] = cert_used
        print (resort_dict[resort]['url'])
        print(element)
        print(cert_used)
    return resort_dict

def test_cert_usage(resort_dict):
    """Goes through all of the resort URLs and identifies which stored ceritifcate (if any) is used 

    Args:
        resort_dict (_dictionary_): 
    """
    for resort in resort_dict:
        response,cert_used = scraper.request_handler(None, resort_dict[resort]['url'])
        print(f"ResortName: {resort_dict[resort]['Name']} \n ResortURL: {resort_dict[resort]['url']} \n Cert_Used: {cert_used}")

def test_dynamic_scrape(resort_dict):
    for resort in resort_dict:
        response,cert_used = scraper.request_handler(None, resort_dict[resort]['url'])
        print(str(cert_used.ok) + '&&' + cert_used.reason)
        soup = BeautifulSoup(response.text, 'html.parser')
        ab = scraper.dynamic_extractor(soup, search_identifier_text="Projected Opening", search_tag='div')

#execution
#test_resort_open(resort_dict)
#resort_dict = test_create_resort_dict(resort_dict)
#test_cert_usage(resort_dict)
test_dynamic_scrape(resort_dict)
print('done')

