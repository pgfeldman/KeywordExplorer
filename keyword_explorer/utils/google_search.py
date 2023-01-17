import urllib.parse
import requests
import os
from datetime import datetime, timedelta
from typing import Dict, List

engines = {
    'com-org-edu': '814dff357c3d046aa',
    'all.com': '017379340413921634422:swl1wknfxia',
    'all.edu': '017379340413921634422:6d0y9yrpnew',
    'all.us': '017379340413921634422:9qwxkhnqoi0',
    'all.gov': '017379340413921634422:lqt7ih7tgci',
    'all.org': '017379340413921634422:ux1lfnmx3ou',
    'scholar': '017379340413921634422:lkfne1rjyay',
    'news': '017379340413921634422:wvavj4i3sbu'
}

class GoogleCSEInfo:
    title:str
    searchTerms:str
    totalResults:int
    count:int
    d:Dict

    def __init__(self, d:Dict):
        self.d = d
        self.title = d['title']
        self.searchTerms = d['searchTerms']
        self.totalResults = d['totalResults']
        self.count = d['count']

    def to_string(self) -> str:
        #return "{}:\n\tlink = {}\n\tsnippet = {}".format(self.title, self.display_link, self.snippet)
        return "{}".format(self.d)


class GoogleCSEResult:
    title:str
    link:str
    display_link:str
    snippet:str
    d:Dict

    def __init__(self, d:Dict):
        self.d = d
        self.title = d['title']
        self.link = d['link']
        self.display_link = d['displayLink']
        self.snippet = d['snippet']

    def to_string(self) -> str:
        #return "{}:\n\tlink = {}\n\tsnippet = {}".format(self.title, self.display_link, self.snippet)
        return "{}".format(self.d)

    def to_html(self) ->str:
        s = '<p>{}</p>\n<ul>\n<li>link = <a href="{}">{}</a></li>\n<li>snippet = {}</li>\n</ul>'.format(
            self.title, self.link, self.display_link, self.snippet
        )
        return s


def get_search_results_list(query:str, engine:str, key:str, arg_dict:Dict = None) -> (List, List):
    info_list = []
    results_list = []
    safe_query = urllib.parse.quote(query)
    #s = "https://www.googleapis.com/customsearch/v1?key={}&cx={}&q=list%20of%20ethnic%20foods".format(key, engine)
    s = "https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}".format(key, engine, safe_query)
    if arg_dict != None:
        for k, v in arg_dict.items():
            s = "{}&{}={}".format(s, k, v)
    print(s)
    r = requests.get(s)
    # print(r)
    if r.status_code == 200:
        j = r.json()
        qd = j['queries']
        for item in qd['request']:
            g = GoogleCSEInfo(item)
            info_list.append(g)
        for item in j['items']:
            g = GoogleCSEResult(item)
            results_list.append(g)
    return (results_list, info_list)

def key_exists(key:str = "GOOGLE_CSE_KEY") -> bool:
    val = os.environ.get(key)
    if val == None:
        return False
    return True

def main():

    engine = engines['com-org-edu']
    key = os.environ.get("GOOGLE_CSE_KEY")
    arg_dict = {"siteSearch":"'twitter.com'", "sort":"date:r:20140815:20140931"}
    lr, li = get_search_results_list("Feldman", engine, key, arg_dict)
    gi:GoogleCSEInfo
    for gi in li:
        print("info: {}".format(gi.to_string()))

    gr:GoogleCSEResult
    for gr in lr:
        #print("\n{}".format(g.to_html()))
        print("result: {}".format(gr.to_string()))

if __name__ == "__main__":
    main()