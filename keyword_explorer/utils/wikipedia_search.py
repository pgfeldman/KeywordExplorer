import unicodedata
import requests
from datetime import datetime, timedelta
import wikipedia
import difflib as dl
from typing import Dict, List

class ViewData:
    project:str
    article:str
    granularity:str
    timestamp:datetime
    views:int

    def __init__(self, d:Dict):
        self.project = d['project']
        self.article = d['article']
        self.granularity = d['granularity']
        self.views = d['views']
        ds = d['timestamp']
        self.timestamp = datetime.strptime(ds, "%Y%m%d00")

    def to_string(self) -> str:
        ds = self.timestamp.strftime("%B %d, %Y (%H:%M:%S)")
        return "project: {}, article: {}, views: {}, timestamp: {} ".format(self.project, self.article, self.views, ds)


def remove_accents(input_str:str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return only_ascii

def get_closet_wiki_page_list(source_term:str, n=3, cutoff=0.6) -> List:
    closest_list = []
    source_term = remove_accents(source_term)
    page_list = wikipedia.search(source_term, suggestion=False)
    if len(page_list) == 0:
        return closest_list
    closest_list = dl.get_close_matches(source_term, page_list, n, cutoff)
    return closest_list

def get_closest_wiki_page(source_term:str, threshold:float = 0.8, debug:bool=True) -> str:
    closest_list = get_closet_wiki_page_list(source_term)

    if debug:
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

def get_pageview_list(page_title:str, start_time:datetime, end_time:datetime, granularity:str = "daily", agent_str:str = "phil@philfeldman.com") -> [List, int]:
    view_list = []
    headers = {"User-Agent": agent_str, "Api-User-Agent":agent_str}
    start_time_str = start_time.strftime("%Y%m%d")
    end_time_str = end_time.strftime("%Y%m%d")
    s = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{}/{}/{}/{}".format(
        page_title, granularity, start_time_str, end_time_str)
    print(s)
    r = requests.get(s, headers=headers)
    # print(r)
    total_views = 0
    if r.status_code == 200:
        for item in r.json()['items']:
            vd = ViewData(item)
            view_list.append(vd)
            total_views += item['views']
            # print("\t{}".format(item))
    else:
        print("Error getting data about '{}' from Wikipedia (Error {}). Views = 0".format(page_title, r.status_code))

    return (view_list, total_views)

def get_wiki_pageviews(page_title:str) -> int:
    yesterday = datetime.today() - timedelta(days=1)
    last_week = yesterday - timedelta(days=7)
    view_list, views = get_pageview_list(page_title=page_title, start_time=last_week, end_time=yesterday)

    vd:ViewData
    for vd in view_list:
        print(vd.to_string())
    print("Weekly views for the page '{}', ending on {} = {:,}".format(page_title, yesterday.strftime("%m/%d/%Y"), views))
    return views

def evaluate(node_name:str, debug:bool = True) -> [str, int]:
    node_name = get_closest_wiki_page(node_name, threshold=0.5, debug=debug)
    node_name = node_name.replace(" ", "_")
    weight = get_wiki_pageviews(node_name)
    return node_name, weight

def main():
    print("wikimedia_scratch")
    l = ["Virtue_ethics", "simpson characters"]
    for key in l:
        node_name, weight = evaluate(key)
        print("{} = {}\n".format(node_name, weight))

if __name__ == "__main__":
    main()