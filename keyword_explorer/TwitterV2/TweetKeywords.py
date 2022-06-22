import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Union
import pprint
from keyword_explorer.utils.MySqlInterface import MySqlInterface


from keyword_explorer.TwitterV2.TwitterV2Base import TwitterV2Base

class TweetData():
    author_id:int
    conversation_id:int
    created_at:str
    id:int
    lang:str
    text:str

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

    def parse_json(self, jd:Dict, filter:bool = False, query_id:int = -1):
        meta = jd['meta']
        data = jd['data']
        for d in data:
            d['query_id'] = query_id
            if filter:
                if self.keyword in d['text']:
                    self.data_list.append(d)
            else:
                self.data_list.append(d)
        print("TweetKeyword.parse_json(): {} got {}/{} tweets".format(self.keyword, self.get_entries(), meta['result_count']))

    def force_dict_value(self, d:Dict, name:str, force):
        if name in d:
            return d[name]
        return force

    def to_db(self, msi:MySqlInterface, max_dt:datetime):
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

                print("\t[{}]: {}".format(count, d))
                count += 1

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


    def get_keywords(self, tk:TweetKeyword, start_dt:datetime, end_dt:datetime = None, tweets_per_sample:int = 10, total_tweets:int = 10, msi:MySqlInterface = None, experiment_id:int = -1):
        #clean up the query so it works with the api
        query = self.prep_query(tk.keyword)
        self.query_list.append(query)
        query_id = -1

        if end_dt == None:
            # The most recent end time has to be ten seconds ago. To be on the safe side, we subtract one minute
            end_dt = datetime.utcnow() - timedelta(minutes=1)
        end_time_str = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        start_time_str = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        print("TweetKeywords.get_keywords() query: '{}', start_time: {}, end_time: {}".format(query, start_time_str, end_time_str))

        end_time_str = end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        start_time_str = start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        time_str = "start_time={}&end_time={}".format(start_time_str, end_time_str)
        print("\t{}".format(time_str))
        url = self. create_keywords_url(query, max_result=tweets_per_sample, time_str=time_str)
        if msi != None:
            sql = "insert into table_query (experiment_id, date_executed, query, keyword, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)"
            vals = (experiment_id, datetime.now(), url, tk.keyword, start_dt, end_dt)
            query_id = msi.write_sql_values_get_row(sql, vals)
        json_response = self.connect_to_endpoint(url)
        tk.parse_json(json_response, query_id)
        next_token = self.parse_json(json_response, total_tweets)
        # self.print_response("Get tk tweets [1] ", json_response)

        count = 2
        while next_token != None and tk.get_entries() < total_tweets:
            url = self. create_keywords_url(query, max_result=tweets_per_sample, time_str=time_str, next_token=next_token)
            if msi != None:
                sql = "insert into table_query (date_executed, query, keyword, start_time, end_time) VALUES (%s, %s, %s, %s, %s)"
                vals = (datetime.now(), url, tk.keyword, start_dt, end_dt)
                query_id = msi.write_sql_values_get_row(sql, vals)
            json_response = self.connect_to_endpoint(url)
            tk.parse_json(json_response, query_id)
            next_token = self.parse_json(json_response, total_tweets)
            # self.print_response("Get tk tweets [{}] ".format(count), json_response)
            count += 1
        if msi != None:
            tk.to_db(msi, end_dt)


def exercise_get_keyword_tweets():
    l = ['chinavirus OR china virus']#, 'covid', 'sars-cov-2', 'china virus', 'virus', 'mask', 'vaccine']
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
        tks.get_keywords(tk, start_dt, end_dt=end_dt, tweets_per_sample=10, total_tweets=30) # tweets_per_sample need to be between 10 - 500
        tk.to_print()

def main():
    # exercise_get_counts()
    exercise_get_keyword_tweets()



if __name__ == "__main__":
    main()