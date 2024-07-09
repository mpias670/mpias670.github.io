import scrape
from config import CSS_SELECTORS, RESORT_DICT, RESORT_NAME_LIST
resort_dict = RESORT_DICT

def test_resort_open(resort_dict):
    
    for idx,resort_name in enumerate(RESORT_NAME_LIST):
        if idx > 51:
            print("Mountain " + resort_name + ": Number " + str(idx) + "/" + str(len(RESORT_NAME_LIST)-1))
            open_status, resort_dict_open = scrape.fetch_resort_open_status(resort_name,resort_dict)
            print(open_status)

def test_create_resort_dict(resort_dict):
    resort_dict = scrape.create_resort_dict(resort_dict)
    return resort_dict

#execution
#test_resort_open(resort_dict)
resort_dict = test_create_resort_dict(resort_dict)