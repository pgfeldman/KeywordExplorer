import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Union
import pprint

import pandas as pd

from keyword_explorer.TwitterV2.TwitterV2Base import TwitterV2Base

class TweetKeyword():
    keyword:str
    data_list:List

    def __init__(self, keyword:str):
        self.keyword = keyword
        self.data_list = []

    def parse_json(self, jd:Dict, filter:bool = False):
        meta = jd['meta']
        data = jd['data']
        for d in data:
            if filter:
                if self.keyword in d['text']:
                    self.data_list.append(d)
            else:
                self.data_list.append(d)
        print("TweetKeyword.parse_json(): {} got {}/{} tweets".format(self.keyword, self.get_entries(), meta['result_count']))

    def get_entries(self) -> int:
        return len(self.data_list)

    def to_print(self, pretty:bool = True):
        print("Keyword = {}".format(self.keyword))
        pp = pprint.PrettyPrinter(indent=4)
        count = 1
        for d in self.data_list:
            if pretty:
                pp.pprint(d)
            else:
                print("\t[{}]: {}".format(count, d))
            count += 1




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
    def create_counts_url(query:str, start_time:str, end_time:str, granularity:str = "day", next_token:str = None):
        url = "https://api.twitter.com/2/tweets/counts/all?query={}&start_time={}&end_time={}&granularity={}".format(
            query, start_time, end_time, granularity)
        if next_token != None:
            url = "{}&next_token={}".format(url, next_token)
        # print("create_counts_url(): {}".format(url))
        return url

    @staticmethod
    def create_keywords_url(query:str, max_result:int = 10, time_str:str = None, next_token:str = None) -> str:
        tweet_fields = "tweet.fields=lang,geo,author_id,in_reply_to_user_id,created_at,conversation_id&expansions=geo.place_id"
        tweet_fields = "&tweet.fields=attachments,lang,author_id,id,text,in_reply_to_user_id,created_at,conversation_id,geo"
        expansion_fields = "&expansions=referenced_tweets.id,referenced_tweets.id.author_id,entities.mentions.username,in_reply_to_user_id,attachments.media_keys"
        media_fields = "&media.fields=preview_image_url,type,url"
        tweet_options = "lang:en -is:retweet"
        url = "https://api.twitter.com/2/tweets/search/all?max_results={}&query={} {}".format(max_result, query, tweet_options)
        url += tweet_fields
        # url += expansion_fields
        # url += media_fields

        if time_str != None:
            url = "{}&{}".format(url, time_str)
        if next_token != None:
            url = "{}&next_token={}".format(url, next_token)
        print("\turl = {}".format(url))
        return url

    def parse_json(self, json_response, num_responses:int) -> Union[str, None]:
        meta:Dict = json_response['meta']
        data:Dict = json_response['data']
        if meta['result_count'] >= num_responses:
            return None
        elif 'next_token' in meta:
            return meta['next_token']

        return None

    def get_keywords_per_day(self, keyword:str, start_dt:datetime, end_dt:datetime = None):
        query = self.prep_query(keyword)
        if end_dt == None:
            end_dt = start_dt + timedelta(days=1)
        end_time_str = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        start_time_str = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        url = self.create_counts_url(query, start_time_str, end_time_str)
        json_response = self.connect_to_endpoint(url)
        # print(json_response)
        meta = json_response['meta']
        if 'total_tweet_count' in meta:
            return int(meta['total_tweet_count'])
        return -1


    def get_keywords(self, tk:TweetKeyword, start_dt:datetime, end_dt:datetime = None, tweets_per_sample:int = 10, skip_days:int = 1, total_tweets:int = 10):
        #clean up the query so it works with the api
        query = self.prep_query(tk.keyword)
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
            tk.parse_json(json_response)
            next_token = self.parse_json(json_response, tweets_per_sample)
            # self.print_response("Get tk tweets [1] ", json_response)

            count = 2
            while next_token != None and tk.get_entries() < total_tweets:
                url = self. create_keywords_url(query, max_result=tweets_per_sample, time_str=time_str, next_token=next_token)
                json_response = self.connect_to_endpoint(url)
                tk.parse_json(json_response)
                next_token = self.parse_json(json_response, tweets_per_sample)
                # self.print_response("Get tk tweets [{}] ".format(count), json_response)
                count += 1

            cur_start = cur_start + timedelta(days=skip_days)
            cur_stop = cur_start + timedelta(days=skip_days)


def exercise_get_keyword_tweets():
    l = ['chinavirus']#, 'covid', 'sars-cov-2', 'china virus', 'virus', 'mask', 'vaccine']
    tks = TweetKeywords()
    date_str = "June 1, 2022 (00:00:00)"
    start_dt = datetime.strptime(date_str, "%B %d, %Y (%H:%M:%S)")
    print("dt = {}".format(start_dt))
    date_str = "June 2, 2022 (00:00:00)"
    end_dt = datetime.strptime(date_str, "%B %d, %Y (%H:%M:%S)")
    for s in l:
        tw = TweetKeyword(keyword=s)
        count = tks.get_keywords_per_day(s, start_dt)
        print("{}: keywords per day = {:,}".format(s, count))
        tks.get_keywords(tw, start_dt, end_dt=end_dt, tweets_per_sample=100, total_tweets=100) # tweets_per_sample need to be between 10 - 500
        tw.to_print()


def main():
    # exercise_get_counts()
    exercise_get_keyword_tweets()



if __name__ == "__main__":
    main()