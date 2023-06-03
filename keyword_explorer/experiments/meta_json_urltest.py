import re
import requests
import json
import os
from typing import Dict


def count_valid_urls(text):
    # Find all URLs using regular expressions
    urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)

    # Test each URL and count valid and invalid ones
    valid_count = 0
    invalid_count = 0
    for url in urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                valid_count += 1
            else:
                invalid_count += 1
        except (requests.exceptions.InvalidURL, requests.exceptions.ConnectionError):
            invalid_count += 1

    return valid_count, invalid_count

def read_json_files(directory_path:str) -> Dict:
    """
    Reads all the json files in the provided directory and places the
    values of the array labeled "experiments" into a Pandas dataframe.
    Returns a dictionary of dataframes, where the key is the filename.
    """
    all_dicts = {}
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            with open(os.path.join(directory_path, filename), 'r') as file:
                json_data = json.load(file)
                all_dicts[filename] = json_data
    return all_dicts

def write_json_files(directory_path, all_dicts:Dict):
    for key, val in all_dicts.items():
        filename = key.replace(".json", "_2.json")
        print("saving {}/{}".format(directory_path, filename))


def evaluate_data(all_dict:Dict):
    print("evaluate_data")
    # go through all the dicts and:
    # 1) Get the index list from the context and explicitly compare those against the numbers in the "context_response" strings
    #   Add a "matched sources" column
    # 2) Get the good URLs and bad URLs for no_context and context responses (4 columns)
    # 3) Add the new data to the dicts
    # 4) Add the bad counts to the summary
    # 5) Write out new json files


def main():
    print("meta_json_urltest")

if __name__ == "__main__":
    main()