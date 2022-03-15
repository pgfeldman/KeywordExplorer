import urllib.parse
import requests
import os
from datetime import datetime, timedelta
from typing import Dict, List

engines = {
    'all.com': '017379340413921634422:swl1wknfxia',
    'all.edu': '017379340413921634422:6d0y9yrpnew',
    'all.us': '017379340413921634422:9qwxkhnqoi0',
    'all.gov': '017379340413921634422:lqt7ih7tgci',
    'all.org': '017379340413921634422:ux1lfnmx3ou',
    'scholar': '017379340413921634422:lkfne1rjyay',
    'news': '017379340413921634422:wvavj4i3sbu'
}

class GoogleCSEResult:
    title:str
    link:str
    display_link:str
    snippet:str

    def __init__(self, d:Dict):
        self.title = d['title']
        self.link = d['link']
        self.display_link = d['displayLink']
        self.snippet = d['snippet']

    def to_string(self) -> str:
        return "{}:\n\tlink = {}\n\tsnippet = {}".format(self.title, self.display_link, self.snippet)

    def to_html(self) ->str:
        s = '<p>{}</p>\n<ul>\n<li>link = <a href="{}">{}</a></li>\n<li>snippet = {}</li>\n</ul>'.format(
            self.title, self.link, self.display_link, self.snippet
        )
        return s


def get_search_results_list(query:str, engine:str, key:str) -> List:
    results_list = []
    safe_query = urllib.parse.quote(query)
    #s = "https://www.googleapis.com/customsearch/v1?key={}&cx={}&q=list%20of%20ethnic%20foods".format(key, engine)
    s = "https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}".format(key, engine, safe_query)
    print(s)
    r = requests.get(s)
    # print(r)
    if r.status_code == 200:
        for item in r.json()['items']:
            g = GoogleCSEResult(item)
            results_list.append(g)
    return results_list

def key_exists(key:str = "GOOGLE_CSE_KEY") -> bool:
    val = os.environ.get(key)
    if val == None:
        return False
    return True

def main():

    engine = engines['all.com']
    key = os.environ.get("GOOGLE_CSE_KEY")
    l = get_search_results_list("slang for COVID-19", engine, key)
    g:GoogleCSEResult
    for g in l:
        print("\n{}".format(g.to_html()))

if __name__ == "__main__":
    main()