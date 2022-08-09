import math
from datetime import datetime, timedelta
import random
import pprint
from keyword_explorer.utils.MySqlInterface import MySqlInterface

from typing import Dict, List, Union


from keyword_explorer.TwitterV2.TwitterV2Base import TwitterV2Base

class TweetData():
    author_id:int
    conversation_id:int
    created_at:str
    id:int
    lang:str
    text:str
    num_entries:int

    def __init__(self, d):
        for key in d:
            if hasattr(self, key):
                setattr(self, key, d[key])

class TweetKeyword():
    keyword:str
    data_list:List
    last_stored_dt:[None, datetime]

    def __init__(self, keyword:str):
        self.keyword = keyword
        self.data_list = []
        self.last_stored_dt = None

    def parse_json(self, jd:Dict, filter:bool = False, query_id:int = -1, clamp = -1) -> bool:
        meta = jd['meta']
        data = jd['data']
        count = 0
        raw_count = 0
        clamped = False
        for d in data:
            raw_count += 1
            d['query_id'] = query_id
            if filter:
                if self.keyword in d['text']:
                    self.data_list.append(d)
            else:
                self.data_list.append(d)
                count += 1
            if clamp > 0 and count > clamp:
                clamped = True
                break

        print("\tTweetKeyword.parse_json() = {}: query_id = {} [{}] got {}/{}, Max = {:,} tweets".format(
            clamped, query_id, self.keyword, count, raw_count, meta['result_count']))
        return clamped

    def force_dict_value(self, d:Dict, name:str, force):
        if name in d:
            return d[name]
        return force

    def to_db(self, msi:MySqlInterface, max_dt:datetime):
        print("\tTweetKeyword.to_db() [{}] writing {:,} items to db".format(self.keyword, len(self.data_list)))
        d:Dict
        count = 1
        for d in self.data_list:
            created_at = datetime.strptime(d['created_at'], '%Y-%m-%dT%H:%M:%S.000Z')
            if created_at < max_dt:
                self.last_stored_dt = created_at
                author_id = self.force_dict_value(d, 'author_id', -1)
                conversation_id = self.force_dict_value(d, 'conversation_id', -1)
                id = self.force_dict_value(d, 'id', -1)
                in_reply_to_user_id = self.force_dict_value(d, 'in_reply_to_user_id', -1)
                lang = self.force_dict_value(d, 'lang', 'NO LANG')
                query_id = self.force_dict_value(d, 'query_id', -1)
                text = self.force_dict_value(d, 'text', 'NO TEXT')

                sql = "insert into table_tweet (query_id, author_id, conversation_id, created_at, in_reply_to_user_id, lang, id, text) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                vals = (query_id, author_id, conversation_id, created_at, in_reply_to_user_id, lang, id, text)
                msi.write_sql_values_get_row(sql, vals)

                # print("\t[{}]: {}".format(count, d))
                count += 1
        self.num_entries = len(self.data_list)
        self.data_list = [] # clear the list so we don't write the same things

    def get_entries(self) -> int:
        n = len(self.data_list)
        if n > 0:
            return n
        return self.num_entries

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
    max_tweets_per_sample = 500
    min_tweets_per_sample = 10

    def __init__(self):
        super().__init__()
        print("TweetKeywords.init()")
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
        # print("\tTweetKeywords.create_keywords_url(): url = {}".format(url))
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


    def get_keywords(self, tk:TweetKeyword, start_dt:datetime, end_dt:datetime = None, tweets_per_sample:int = 10, tweets_to_download:int = 10, msi:MySqlInterface = None, experiment_id:int = -1) :
        #clean up the query so it works with the api
        query = self.prep_query(tk.keyword)
        self.query_list.append(query)
        query_id = -1

        if end_dt == None:
            # The most recent end time has to be ten seconds ago. To be on the safe side, we subtract one minute
            end_dt = datetime.utcnow() - timedelta(minutes=1)
        end_time_str = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        start_time_str = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        # print("TweetKeywords.get_keywords() query: '{}', start_time: {}, end_time: {}".format(query, start_time_str, end_time_str))

        end_time_str = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        start_time_str = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        time_str = "start_time={}&end_time={}".format(start_time_str, end_time_str)
        # print("\t{}".format(time_str))
        url = self.create_keywords_url(query, max_result=min(tweets_per_sample, tweets_to_download), time_str=time_str)
        if msi != None:
            sql = "insert into table_query (experiment_id, date_executed, query, keyword, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)"
            vals = (experiment_id, datetime.now(), url, tk.keyword, start_dt, end_dt)
            query_id = msi.write_sql_values_get_row(sql, vals)
        # print("query_id = {}, url = {}".format(query_id, url))
        # next_token = None
        json_response = self.connect_to_endpoint(url)
        tk.parse_json(json_response, query_id=query_id, clamp=tweets_per_sample)
        next_token = self.parse_json(json_response, tweets_to_download)
        # self.print_response("Get tk tweets [1] ", json_response)

        count = 2
        max_result = min(tweets_per_sample, tweets_to_download)
        while next_token != None and tk.get_entries() < max_result:
            url = self. create_keywords_url(query, max_result=tweets_per_sample, time_str=time_str, next_token=next_token)
            if msi != None:
                sql = "insert into table_query (experiment_id, date_executed, query, keyword, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)"
                vals = (experiment_id, datetime.now(), url, tk.keyword, start_dt, end_dt)
                query_id = msi.write_sql_values_get_row(sql, vals)
            json_response = self.connect_to_endpoint(url)
            tk.parse_json(json_response, query_id=query_id, clamp=tweets_per_sample)
            next_token = self.parse_json(json_response, tweets_to_download)
            print("\ttk.get_entries() = {}, max_result = {}".format(tk.get_entries(), max_result))
            # self.print_response("Get tk tweets [{}] ".format(count), json_response)
            count += 1
        if msi != None:
            tk.to_db(msi, end_dt)

    def sample_keywords_one_day(self, tk:TweetKeyword, start_dt:datetime, tweets_available:int, clamp:int, tweets_per_sample:int, msi:MySqlInterface = None, experiment_id:int = -1):
        date_fmt = "%B %d, %Y (%H:%M:%S)"
        twitter_fmt = '%Y-%m-%dT%H:%M:%SZ'

        # default is to get the entire day
        stop_dt = start_dt + timedelta(days=0.9999)
        query = self.prep_query(tk.keyword)
        self.query_list.append(query)
        query_id = -1

        tweets_to_download = min(clamp, tweets_available)
        print("tweets_to_download = {:,}".format(tweets_to_download))

        ratio = tweets_to_download / tweets_available
        print("ratio = {:.2f}".format(ratio))

        if ratio < 1.0:
            print("ratio < 1.0 - sample across the day")
            num_pulls = math.ceil(tweets_to_download / tweets_per_sample)
            print("num_pulls of {} = {}".format(tweets_per_sample, num_pulls))
            remaining = tweets_to_download
            for i in range(num_pulls):
                print("\n\tPass {}".format(i))
                span = (1.0 - ratio*num_pulls)/num_pulls
                print("\tspan = {:.2f}".format(span))

                start_offset = span * random.random()
                start_dt = start_dt + timedelta(days = start_offset)
                stop_dt = start_dt + timedelta(days=ratio)

                print("\tStart date = {}".format(start_dt.strftime(date_fmt)))
                print("\tEnd date = {}".format(stop_dt.strftime(date_fmt)))
                end_time_str = stop_dt.strftime(twitter_fmt)
                start_time_str = start_dt.strftime(twitter_fmt)
                time_str = "start_time={}&end_time={}".format(start_time_str, end_time_str)
                pull = min(remaining, tweets_per_sample)
                pull = max(self.min_tweets_per_sample, pull) # don
                print("\tDownloading {} tweets".format(pull))

                url = self.create_keywords_url(query, max_result=pull, time_str=time_str)
                if msi != None:
                    sql = "insert into table_query (experiment_id, date_executed, query, keyword, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)"
                    vals = (experiment_id, datetime.now(), url, tk.keyword, start_dt, stop_dt)
                    query_id = msi.write_sql_values_get_row(sql, vals)

                json_response = self.connect_to_endpoint(url)
                tk.parse_json(json_response, query_id=query_id, clamp=tweets_per_sample)
                next_token = self.parse_json(json_response, tweets_to_download)
                remaining -= tweets_per_sample
                start_dt = stop_dt

        else:
            print("ratio > 1.0 - get the entire day")
            # get the entire day
            stop_dt = start_dt + timedelta(days=0.9999)
            print("Start date = {}".format(start_dt.strftime(date_fmt)))
            print("End date = {}".format(stop_dt.strftime(date_fmt)))
            end_time_str = stop_dt.strftime(twitter_fmt)
            start_time_str = start_dt.strftime(twitter_fmt)
            time_str = "start_time={}&end_time={}".format(start_time_str, end_time_str)
            url = self.create_keywords_url(query, max_result=tweets_to_download, time_str=time_str)
            if msi != None:
                sql = "insert into table_query (experiment_id, date_executed, query, keyword, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)"
                vals = (experiment_id, datetime.now(), url, tk.keyword, start_dt, stop_dt)
                query_id = msi.write_sql_values_get_row(sql, vals)
            # print("query_id = {}, url = {}".format(query_id, url))
            # next_token = None
            json_response = self.connect_to_endpoint(url)
            tk.parse_json(json_response, query_id=query_id, clamp=clamp)

        if msi != None:
            tk.to_db(msi, stop_dt)
        return tk.get_entries()


def exercise_get_keyword_tweets():
    l = ['chinavirus OR china virus']#, 'covid', 'sars-cov-2', 'china virus', 'virus', 'mask', 'vaccine']
    l = ['ivermectin', 'paxlovid']
    tks = TweetKeywords()
    date_str = "June 1, 2022 (00:00:00)"
    start_dt = datetime.strptime(date_str, "%B %d, %Y (%H:%M:%S)")
    print("dt = {}".format(start_dt))
    date_str = "June 2, 2022 (00:00:00)"
    end_dt = datetime.strptime(date_str, "%B %d, %Y (%H:%M:%S)")
    for s in l:
        tk = TweetKeyword(keyword=s)
        count = tks.get_keywords_per_day(s, start_dt)
        print("{}: keywords per day = {:,}".format(s, count))
        tks.get_keywords(tk, start_dt, end_dt=end_dt, tweets_per_sample=10, tweets_to_download=30) # tweets_per_sample need to be between 10 - 500
        tk.to_print()

def exercise_sample_keywords_one_day():
    tweets_available = 2000
    clamp = 1234
    tweets_per_sample = 500
    l = ['ivermectin', 'paxlovid']
    tks = TweetKeywords()
    date_str = "June 1, 2022 (00:00:00)"
    start_dt = datetime.strptime(date_str, "%B %d, %Y (%H:%M:%S)")
    print("dt = {}".format(start_dt))
    date_str = "June 2, 2022 (00:00:00)"
    end_dt = datetime.strptime(date_str, "%B %d, %Y (%H:%M:%S)")
    for s in l:
        tk = TweetKeyword(keyword=s)
        count = tks.sample_keywords_one_day(tk, start_dt, tweets_available, clamp, tweets_per_sample)
        print("{}: keywords per day = {:,}".format(s, count))
        tks.get_keywords(tk, start_dt, end_dt=end_dt, tweets_per_sample=10, tweets_to_download=30) # tweets_per_sample need to be between 10 - 500
        tk.to_print()

def main():
    # exercise_get_counts()
    # exercise_get_keyword_tweets()
    exercise_sample_keywords_one_day()



if __name__ == "__main__":
    main()