import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime, timedelta
from typing import Dict, List, Union

import pandas as pd

from keyword_explorer.TwitterV2.TwitterV2Base import TwitterV2Base

class TwitterV2Count:
    end_time:datetime
    start_time:datetime
    count:int

    def __init__(self, d:Dict):
        self.start_time = datetime.strptime(d['start'], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.end_time = datetime.strptime(d['end'], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.count = int(d['tweet_count'])
    
    def to_string(self) -> str:
        return "start: {}, end: {}, count: {}".format(self.start_time.strftime("%B %d, %Y (%H:%M:%S)"),
                self.end_time.strftime("%B %d, %Y (%H:%M:%S)"), self.count)


class TwitterV2Counts (TwitterV2Base):
    total_tweets:int
    count_list:List
    multi_count_list:List
    query_list:List
    totals_dict:Dict

    def __init__(self):
        super().__init__()
        #print("TwitterV2Counts, token = {}".format(self.bearer_token))
        self.reset()
        # self.bearer_token = os.environ.get("BEARER_TOKEN_2")

    def reset(self):
        self.query = None
        self.count_list = []
        self.query_list = []
        self.multi_count_list = []
        self.total_tweets = 0
        self.totals_dict = {}

    def parse_json(self, json_response) -> Union[str, None]:
        meta:Dict = json_response['meta']
        data:Dict = json_response['data']
        for d in data:
            tvc = TwitterV2Count(d)
            self.total_tweets += tvc.count
            self.count_list.append(tvc)

        if 'next_token' in meta:
            return meta['next_token']

        return None

    def get_query_totals(self, query:str):
        totals = 0
        tvc:TwitterV2Count
        for tvc in self.count_list:
            totals += tvc.count
        self.totals_dict[query] = totals

    def get_sampled_counts(self, query:str, start_time:datetime, end_time:datetime = None, skip_days:int=3, tweet_options:str = "lang:en -is:retweet"):
        self.count_list = []

        #clean up the query so it works with the api
        query = self.prep_query(query)
        self.query_list.append(query)

        if end_time == None:
            # The most recent end time has to be ten seconds ago. To be on the safe side, we subtract one minute
            end_time = datetime.utcnow() - timedelta(minutes=1)
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        print("query: '{}', start_time: {}, end_time: {} skip_days:{}".format(query, start_time_str, end_time_str, skip_days))

        cur_start = start_time
        while cur_start < end_time:
            cur_stop = cur_start + timedelta(days=1)
            end_time_str = cur_stop.strftime('%Y-%m-%dT%H:%M:%SZ')
            start_time_str = cur_start.strftime('%Y-%m-%dT%H:%M:%SZ')
            print("\tstart_time: {}, end_time: {}".format(start_time_str, end_time_str))
            url = self.create_counts_url(query, start_time_str, end_time_str, tweet_options=tweet_options)
            json_response = self.connect_to_endpoint(url)
            print(json_response)
            self.parse_json(json_response)
            cur_start = cur_start + timedelta(days=skip_days)
        self.count_list = sorted(self.count_list, key=lambda x: x.start_time)
        self.multi_count_list.append(self.count_list)
        self.get_query_totals(query)

    def get_counts(self, query:str, start_time:datetime, end_time:datetime = None, granularity:str = "day", tweet_options:str = "lang:en -is:retweet"):
        self.count_list = []

        #clean up the query so it works with the api
        query = self.prep_query(query)
        self.query_list.append(query)

        if end_time == None:
            # The most recent end time has to be ten seconds ago. To be on the safe side, we subtract one minute
            end_time = datetime.utcnow() - timedelta(minutes=1)
        end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        print("query: '{}', start_time: {}, end_time: {}".format(query, start_time_str, end_time_str, granularity=granularity))

        url = self.create_counts_url(query, start_time_str, end_time_str, tweet_options=tweet_options)
        json_response = self.connect_to_endpoint(url)
        next_token = self.parse_json(json_response)
        print("[1]: {}".format(url))

        count:int = 2
        while next_token != None:
            url = self.create_counts_url(query, start_time_str, end_time_str, granularity=granularity, next_token=next_token, tweet_options=tweet_options)
            json_response = self.connect_to_endpoint(url)
            next_token = self.parse_json(json_response)
            print("[{}]: {}".format(count, url))
            count += 1

        self.count_list = sorted(self.count_list, key=lambda x: x.start_time)
        self.multi_count_list.append(self.count_list)
        self.get_query_totals(query)

    @staticmethod
    def create_counts_url(query:str, start_time:str, end_time:str, granularity:str = "day", next_token:str = None, tweet_options:str = "lang:en -is:retweet"):
        url = "https://api.twitter.com/2/tweets/counts/all?query={} {}&start_time={}&end_time={}&granularity={}".format(
            query, tweet_options, start_time, end_time, granularity)
        if next_token != None:
            url = "{}&next_token={}".format(url, next_token)
        # print("create_counts_url(): {}".format(url))
        return url

    def print(self):
        tvc:TwitterV2Count
        for tvc in self.count_list:
            print(tvc.to_string())
        print("Total tweets for query '{}' = {:,}".format(self.query, self.total_tweets))


    def plot(self):
        count_list:List
        plt.title("query = '{}', {:,} tweets".format(self.query_list, self.total_tweets))
        # TODO: Fix the indexing so that colors and title use the repeating colors and text
        ci = 0
        # l1 = list(mcolors.TABLEAU_COLORS.values())
        for count_list in self.multi_count_list:
            y_vals = []
            dates = []
            tvc:TwitterV2Count
            for tvc in count_list:
                y_vals.append(tvc.count+1)
                dates.append(tvc.start_time)
            plt.plot(dates, y_vals)
            ci += 1
        plt.yscale("log")
        # plt.gca().legend(self.query_list)
        plt.gca().legend(["{}: {:,}".format(k, v) for k, v in self.totals_dict.items()])
        plt.gcf().autofmt_xdate()
        plt.show()

    def to_dataframe(self, excel_fmt:bool = False) -> pd.DataFrame:
        l = []
        for i in range(len(self.multi_count_list)):
            query = self.query_list[i]
            count_list = self.multi_count_list[i]
            tvc:TwitterV2Count
            d = {"keyword":query}
            l.append(d)
            for tvc in count_list:
                if excel_fmt:
                    start_time_str = tvc.start_time.strftime('%m/%d/%Y %H:%M')
                else:
                    start_time_str = tvc.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                d[start_time_str] = tvc.count
        df = pd.DataFrame(l)
        return df

    def to_spreadsheet(self, filename:str):
        df = self.to_dataframe(True)
        writer = pd.ExcelWriter(filename)
        df.to_excel("Counts")


def exercise_get_counts():
    l = ['covid', 'sars-cov-2', 'chinavirus', 'virus', 'mask', 'vaccine']
    tc = TwitterV2Counts()
    date_str = "January 1, 2020 (00:00:00)"
    start_dt = datetime.strptime(date_str, "%B %d, %Y (%H:%M:%S)")
    print("dt = {}".format(start_dt))
    date_str = "March 1, 2020 (00:00:00)"
    end_dt = datetime.strptime(date_str, "%B %d, %Y (%H:%M:%S)")
    for s in l:
        tc.get_counts(s, start_dt, end_time=end_dt)
    tc.plot()
    df = tc.to_dataframe()
    print(df)

def exercise_get_sampled_counts():
    l = ['covid', 'sars-cov-2', 'chinavirus', 'virus', 'mask', 'vaccine']
    tc = TwitterV2Counts()
    date_str = "January 1, 2020 (00:00:00)"
    start_dt = datetime.strptime(date_str, "%B %d, %Y (%H:%M:%S)")
    print("dt = {}".format(start_dt))
    date_str = "February 1, 2020 (00:00:00)"
    end_dt = datetime.strptime(date_str, "%B %d, %Y (%H:%M:%S)")
    for s in l:
        tc.get_sampled_counts(s, start_dt, end_time=end_dt, skip_days=30)
    tc.plot()
    df = tc.to_dataframe()
    print(df)



def main():
    # exercise_get_counts()
    exercise_get_sampled_counts()



if __name__ == "__main__":
    main()