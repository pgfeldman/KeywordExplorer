import math
from datetime import datetime, timedelta
import random
import pprint
import re
from keyword_explorer.utils.MySqlInterface import MySqlInterface

from typing import Dict, List, Union, Any


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
        clamped = False
        count = 0
        raw_count = 0
        meta = jd['meta']
        if 'data' in jd:
            data = jd['data']
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
        if 'meta' in jd:
            print("\tTweetKeyword.parse_json() = {}: query_id = {} [{}] got {}/{}, Max = {:,} tweets".format(
                clamped, query_id, self.keyword, count, raw_count, meta['result_count']))
        return clamped

    def force_dict_value(self, d:Dict, name:str, force):
        if name in d:
            return d[name]
        return force

    def to_db(self, msi:MySqlInterface, max_dt:datetime = None):
        print("\tTweetKeyword.to_db() [{}] writing {:,} items to db".format(self.keyword, len(self.data_list)))
        d:Dict
        count = 1
        for d in self.data_list:
            created_at = datetime.strptime(d['created_at'], '%Y-%m-%dT%H:%M:%S.000Z')
            if max_dt == None or created_at < max_dt:
                is_thread = False
                if max_dt == None:
                    is_thread = True
                self.last_stored_dt = created_at
                author_id = self.force_dict_value(d, 'author_id', -1)
                conversation_id = self.force_dict_value(d, 'conversation_id', -1)
                id = self.force_dict_value(d, 'id', -1)
                in_reply_to_user_id = self.force_dict_value(d, 'in_reply_to_user_id', -1)
                lang = self.force_dict_value(d, 'lang', 'NO LANG')
                query_id = self.force_dict_value(d, 'query_id', -1)
                text = self.force_dict_value(d, 'text', 'NO TEXT')

                sql = "replace into table_tweet (query_id, author_id, conversation_id, created_at, in_reply_to_user_id, lang, id, text, is_thread) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                vals = (query_id, author_id, conversation_id, created_at, in_reply_to_user_id, lang, id, text, is_thread)
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
                print("\n-----------\nTweet [{}], keyword = {}".format(count, self.keyword))
                pp.pprint(d)
            else:
                print("\t[{}]: {}".format(count, d))
            count += 1




class TweetKeywords(TwitterV2Base):
    max_tweets_per_sample = 500
    min_tweets_per_sample = 10
    query_params:Union[str, None]

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
        self.query_params = None

    # @staticmethod
    def create_counts_url(self, query:str, start_time:str, end_time:str, granularity:str = "day", next_token:str = None):
        url = "https://api.twitter.com/2/tweets/counts/all?query={}&start_time={}&end_time={}&granularity={}".format(
            query, start_time, end_time, granularity)
        if next_token != None:
            url = "{}&next_token={}".format(url, next_token)
        # print("create_counts_url(): {}".format(url))
        return url

    # @staticmethod
    def create_keywords_url(self, query:str, max_result:int = 10, time_str:str = None, next_token:str = None) -> str:
        tweet_fields = "tweet.fields=lang,geo,author_id,in_reply_to_user_id,created_at,conversation_id&expansions=geo.place_id"
        tweet_fields = "&tweet.fields=attachments,lang,author_id,id,text,in_reply_to_user_id,created_at,conversation_id,geo"
        expansion_fields = "&expansions=referenced_tweets.id,referenced_tweets.id.author_id,entities.mentions.username,in_reply_to_user_id,attachments.media_keys"
        media_fields = "&media.fields=preview_image_url,type,url"
        tweet_options = "place_country:US lang:en -is:retweet"
        if self.query_params != None:
            tweet_options = self.query_params
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

    def set_query_params(self, params:str = 'place_country:US lang:en -is:retweet'):
        self.query_params = params

    def create_historical_conversation_url(self, conversation_id:str, max_result:int = 10, next_token:str = None) -> str:
        tweet_fields = "tweet.fields=lang,author_id,in_reply_to_user_id,created_at,conversation_id"
        tweet_options = "place_country:US lang:en -is:retweet"
        if self.query_params != None:
            tweet_options = self.query_params
        url = "https://api.twitter.com/2/tweets/search/all?max_results={}&query=conversation_id:{} " \
              "{}&{}".format(
            max_result, conversation_id, tweet_options, tweet_fields)
        # print(url)
        if next_token != None:
            url = "{}&next_token={}".format(url, next_token)
        return url

    # Takes a comma separated list of user IDs. Up to 100 are allowed in a single request.
    # Make sure to not include a space between commas and fields.
    def create_user_url(self, user_id:str) -> str:
        user_fields = "location,name,username,verified&expansions=pinned_tweet_id"
        user_fields = "created_at,description,location,name,username,verified"
        url = "https://api.twitter.com/2/users?ids={}&user.fields={}".format(user_id, user_fields)
        return url

    def create_bookmark_url(self, user_id:str) -> str:
        url = "https://api.twitter.com/2/users/{}/bookmarks".format(user_id)
        return url

    def parse_json(self, json_response, num_responses:int) -> Union[str, None]:
        if 'meta' in json_response:
            meta:Dict = json_response['meta']
            if meta['result_count'] >= num_responses:
                return None
            elif 'next_token' in meta:
                return meta['next_token']

        return None

    def safe_dict(self, d:Dict, name:str, default:Any=None) -> Any:
        if name in d:
            return d[name]
        return default

        # The meat of a twitter query and processing
    def run_thread_query(self, tk:TweetKeyword, conversation_id:str, tweets_per_sample:int, tweets_to_download:int,
                  next_token:str = None, experiment_id:int = -1, msi:MySqlInterface = None) -> str:
        query_id = -1
        url = self. create_historical_conversation_url(conversation_id, max_result=tweets_per_sample, next_token=next_token)
        if msi != None:
            sql = "insert into table_query (experiment_id, date_executed, query, keyword) VALUES (%s, %s, %s, %s)"
            vals = (experiment_id, datetime.now(), url, tk.keyword)
            query_id = msi.write_sql_values_get_row(sql, vals)
            print("run_thread_query() INSERT response = {}".format(query_id))
        json_response = self.connect_to_endpoint(url)
        tk.parse_json(json_response, query_id=query_id, clamp=tweets_per_sample)
        next_token = self.parse_json(json_response, tweets_to_download)

        if msi != None:
            tk.to_db(msi)
        if tk.get_entries() > tweets_to_download:
            return None
        return next_token

    # The meat of a twitter query and processing
    def run_query(self, tk:TweetKeyword, query:str, tweets_per_sample:int, tweets_to_download:int,
                  start_dt:datetime, end_dt:datetime, next_token:str = None, experiment_id:int = -1, msi:MySqlInterface = None) -> str:
        query_id = -1
        end_time_str = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        start_time_str = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        time_str = "start_time={}&end_time={}".format(start_time_str, end_time_str)
        url = self. create_keywords_url(query, max_result=tweets_per_sample, time_str=time_str, next_token=next_token)
        if msi != None:
            sql = "insert into table_query (experiment_id, date_executed, query, keyword, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)"
            vals = (experiment_id, datetime.now(), url, tk.keyword, start_dt, end_dt)
            query_id = msi.write_sql_values_get_row(sql, vals)
        json_response = self.connect_to_endpoint(url)
        tk.parse_json(json_response, query_id=query_id, clamp=tweets_per_sample)
        next_token = self.parse_json(json_response, tweets_to_download)
        return next_token

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
        next_token = self.run_query(tk, query, tweets_per_sample, tweets_to_download, start_dt, end_dt, None, experiment_id, msi)
        # self.print_response("Get tk tweets [1] ", json_response)

        count = 2
        max_result = min(tweets_per_sample, tweets_to_download)
        while next_token != None and tk.get_entries() < max_result:
            next_token = self.run_query(tk, query, tweets_per_sample, tweets_to_download, start_dt, end_dt, None, experiment_id, msi)
            print("\ttk.get_entries() = {}, max_result = {}".format(tk.get_entries(), max_result))
            # self.print_response("Get tk tweets [{}] ".format(count), json_response)
            count += 1
        if msi != None:
            tk.to_db(msi, end_dt)

    def sample_keywords_one_day(self, tk:TweetKeyword, start_dt:datetime, tweets_available:int, clamp:int, tweets_per_sample:int,
                                msi:MySqlInterface = None, experiment_id:int = -1) -> int:
        date_fmt = "%B %d, %Y (%H:%M:%S)"
        twitter_fmt = '%Y-%m-%dT%H:%M:%SZ'

        # default is to get the entire day
        stop_dt = start_dt + timedelta(days=0.9999)
        query = self.prep_query(tk.keyword)
        self.query_list.append(query)
        query_id = -1

        tweets_to_download = min(clamp, tweets_available)
        print("tweets_to_download = {:,}".format(tweets_to_download))
        if tweets_to_download == 0:
            tk.num_entries = 0
            return 0

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
                # stop_dt = start_dt + timedelta(days=ratio)
                stop_dt = start_dt + timedelta(days=.9999)

                print("\tStart date = {}".format(start_dt.strftime(date_fmt)))
                print("\tEnd date = {}".format(stop_dt.strftime(date_fmt)))
                next_token = self.run_query(tk, query, tweets_per_sample, tweets_to_download, start_dt, stop_dt, None, experiment_id, msi)
                remaining -= tweets_per_sample
                start_dt = stop_dt

        else:
            print("ratio > 1.0 - get the entire day")
            # get the entire day
            stop_dt = start_dt + timedelta(days=0.9999)
            print("Start date = {}".format(start_dt.strftime(date_fmt)))
            print("End date = {}".format(stop_dt.strftime(date_fmt)))
            next_token = self.run_query(tk, query, tweets_per_sample, tweets_to_download, start_dt, stop_dt, None, experiment_id, msi)

        if msi != None:
            tk.to_db(msi, stop_dt)
        return tk.get_entries()

    def run_user_query(self, id_list:List, msi:MySqlInterface):
        dt_format = '%Y-%m-%dT%H:%M:%S.000Z'
        s:str = ",".join(map(str, id_list))
        url = self.create_user_url(s)
        json_response = self.connect_to_endpoint(url)
        data:List = json_response['data']
        d:Dict
        for d in data:
            created_at = datetime.strptime(d['created_at'], dt_format)
            description = self.safe_dict(d, 'description')
            description = description.encode("utf-8", "replace")
            id = d['id']
            location = self.safe_dict(d, 'location')
            name = self.safe_dict(d, 'name')
            username = self.safe_dict(d, 'username')
            verified = True if d['verified'] == 'true' else False
            sql = "replace into twitter_v2.table_user (id, created_at, description, location, name, username, verified) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            vals = (id, created_at, description, location, name, username, verified)
            msi.write_sql_values_get_row(sql, vals)


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

def exercise_get_threads():
    test_conversation = "1561906311125680138"
    print("conversation_id = [{}]".format("1561906311125680138"))
    tks = TweetKeywords()
    tk = TweetKeyword(keyword="foo") # we'd get this from the database along with conversation_id
    next_token = tks.run_thread_query(tk, conversation_id=test_conversation, tweets_per_sample=10, tweets_to_download=100)
    count = 0
    while next_token != None:
        print("next_token = {}".format(next_token))
        next_token = tks.run_thread_query(tk, conversation_id=test_conversation, tweets_per_sample=10, tweets_to_download=100, next_token=next_token)
        count += 1
        if count > 5:
            break
    tk.to_print()

def exercise_get_bookmarks():
    user_id = "836938832"
    tks = TweetKeywords()
    url = tks.create_bookmark_url(user_id)
    print(url)
    json_response = tks.connect_to_endpoint(url)
    print(json_response)

def main():
    # exercise_get_counts()
    exercise_get_keyword_tweets()
    # exercise_sample_keywords_one_day()
    # exercise_get_threads()
    # exercise_get_bookmarks()



if __name__ == "__main__":
    main()