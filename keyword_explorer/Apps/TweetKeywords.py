import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Union

import pandas as pd

from keyword_explorer.TwitterV2.TwitterV2Base import TwitterV2Base

class TweetKeyword():
    start_time:datetime
    keyword:str

    def __init__(self, d:Dict):
        self.keyword = d['keyword']



class TweetKeywords(TwitterV2Base):
    start_time:datetime

    def __init__(self):
        super().__init__()
        print("TweetKeywords, token = {}".format(self.bearer_token))
        self.reset()

    def reset(self):
        self.query = None
        self.count_list = []
        self.query_list = []
        self.multi_count_list = []
        self.total_tweets = 0
        self.totals_dict = {}

    @staticmethod
    def create_keywords_url(query:str, max_result:int = 10, time_str:str = None, next_token:str = None) -> str:
        tweet_fields = "tweet.fields=lang,geo,author_id,in_reply_to_user_id,created_at,conversation_id&expansions=geo.place_id"
        tweet_fields = "tweet.fields=lang,author_id,in_reply_to_user_id,created_at,conversation_id"
        tweet_options = "lang:en"
        url = "https://api.twitter.com/2/tweets/search/all?max_results={}&query={} {}&{}".format(max_result, query, tweet_options, tweet_fields)
        if time_str != None:
            url = "{}&{}".format(url, time_str)
        if next_token != None:
            url = "{}&next_token={}".format(url, next_token)
        print("max_result = {}\nurl = {}".format(max_result, url))
        return url

    def parse_json(self, json_response, num_responses:int) -> Union[str, None]:
        meta:Dict = json_response['meta']
        data:Dict = json_response['data']
        if meta['result_count'] >= num_responses:
            return None
        elif 'next_token' in meta:
            return meta['next_token']

        return None

    def get_keywords(self, keyword:str, start_dt:datetime, end_dt:datetime = None, tweets_per_sample:int = 10, skip_days:int = 1):
        #clean up the query so it works with the api
        query = self.prep_query(keyword)
        self.query_list.append(query)

        if end_dt == None:
            # The most recent end time has to be ten seconds ago. To be on the safe side, we subtract one minute
            end_dt = datetime.utcnow() - timedelta(minutes=1)
        end_time_str = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        start_time_str = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        print("query: '{}', start_time: {}, end_time: {} skip_days:{}".format(query, start_time_str, end_time_str, skip_days))

        cur_start = start_dt
        cur_stop = cur_start + timedelta(days=skip_days)
        while cur_start < end_dt:
            end_time_str = cur_stop.strftime('%Y-%m-%dT%H:%M:%SZ')
            start_time_str = cur_start.strftime('%Y-%m-%dT%H:%M:%SZ')
            time_str = "start_time={}&end_time={}".format(start_time_str, end_time_str)
            print("\t{}".format(time_str))
            url = self. create_keywords_url(query, max_result=tweets_per_sample, time_str=time_str)
            json_response = self.connect_to_endpoint(url)
            next_token = self.parse_json(json_response, tweets_per_sample)
            self.print_response("Get keyword tweets [1] ", json_response)

            count = 2
            while next_token != None:
                url = self. create_keywords_url(query, max_result=tweets_per_sample, time_str=time_str, next_token=next_token)
                json_response = self.connect_to_endpoint(url)
                next_token = self.parse_json(json_response, tweets_per_sample)
                self.print_response("Get keyword tweets [{}] ".format(count), json_response)
                count += 1

            cur_start = cur_start + timedelta(days=skip_days)
            cur_stop = cur_start + timedelta(days=skip_days)


def exercise_get_keyword_tweets():
    l = ['china virus']#, 'covid', 'sars-cov-2', 'chinavirus', 'virus', 'mask', 'vaccine']
    tk = TweetKeywords()
    date_str = "June 1, 2022 (00:00:00)"
    start_dt = datetime.strptime(date_str, "%B %d, %Y (%H:%M:%S)")
    print("dt = {}".format(start_dt))
    date_str = "June 6, 2022 (00:00:00)"
    end_dt = datetime.strptime(date_str, "%B %d, %Y (%H:%M:%S)")
    for s in l:
        tk.get_keywords(s, start_dt, end_dt=end_dt, tweets_per_sample=10) # tweets_per_sample need to be between 10 - 500


def main():
    # exercise_get_counts()
    exercise_get_keyword_tweets()



if __name__ == "__main__":
    main()