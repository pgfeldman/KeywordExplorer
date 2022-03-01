import unicodedata
import requests
from datetime import datetime, timedelta
import wikipedia
import difflib as dl
from typing import Dict, List

def remove_accents(input_str:str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return only_ascii

def get_closest_wiki_page(source_term:str, threshold:float = 0.8, debug:bool=True) -> str:
    source_term = remove_accents(source_term)
    page_list = wikipedia.search(source_term, suggestion=False)
    if len(page_list) == 0:
        return source_term
    closest_list = dl.get_close_matches(source_term, page_list)
    if debug:
        print("source_term = {}, page_list = [{}]".format(source_term, ", ".join(page_list)))
        print("source_term = {}, closest_list = [{}]".format(source_term, ", ".join(closest_list)))
    if len(closest_list) == 0:
        return source_term
    ratio = dl.SequenceMatcher(None, source_term, closest_list[0]).quick_ratio()
    if debug:
        print("{} - {} ratio = {}, threshold = {}".format(source_term, closest_list[0], ratio, threshold))
    if ratio > threshold:
        if debug:
            print("Changing {} to {}".format(source_term, closest_list[0]))
        source_term = closest_list[0]
    return remove_accents(source_term)

def get_wiki_pageviews(page_title:str) -> int:
    headers = {"User-Agent": "phil@philfeldman.com", "Api-User-Agent":"phil@philfeldman.com"}
    yesterday = datetime.today() - timedelta(days=1)
    last_week = yesterday - timedelta(days=7)
    yester_s = yesterday.strftime("%Y%m%d")
    lastw_s = last_week.strftime("%Y%m%d")
    s = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{}/daily/{}/{}".format(
        page_title, lastw_s, yester_s)
    print(s)
    r = requests.get(s, headers=headers)
    # print(r)
    views = 0
    if r.status_code == 200:
        for item in r.json()['items']:
            views += item['views']
            # print("\t{}".format(item))
        print("Weekly views for the page '{}', ending on {} = {:,}".format(page_title, yesterday.strftime("%m/%d/%Y"), views))
    else:
        print("Error getting data about '{}' from Wikipedia (Error {}). Views = 0".format(page_title, r.status_code))
    return views

def evaluate(node_name:str, debug:bool = True) -> [str, int]:
    node_name = get_closest_wiki_page(node_name, threshold=0.5, debug=debug)
    node_name = node_name.replace(" ", "_")
    weight = get_wiki_pageviews(node_name)
    return node_name, weight

def main():
    print("wikimedia_scratch")
    l = ["Virtue_ethics", "Virtue Ethics"]
    for key in l:
        node_name, weight = evaluate(key)
        print("{} = {}\n".format(node_name, weight))

if __name__ == "__main__":
    main()