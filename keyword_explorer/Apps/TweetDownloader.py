import random
import time
import tkinter as tk
import tkinter.messagebox as message
from datetime import datetime, timedelta
from tkinter import filedialog

import pandas as pd

from keyword_explorer.Apps.AppBase import AppBase
from keyword_explorer.TwitterV2.TweetKeywords import TweetKeywords, TweetKeyword
from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.Checkboxes import Checkboxes, DIR
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.DateEntryField import DateEntryField
from keyword_explorer.tkUtils.ToolTip import ToolTip
from keyword_explorer.tkUtils.TextField import TextField

from keyword_explorer.utils.MySqlInterface import MySqlInterface

from typing import Dict, List, Callable

class KeywordData:
    num_tweets:int
    name:str
    def __init__(self, name:str, tweets:int = 0):
        self.reset(name, tweets)

    def reset(self, name:str, tweets:int):
        self.name = name
        self.num_tweets = tweets

    def add_to_num_tweets(self, val:int):
        print("KeywordData: {} adding {} to {} = {}".format(self.name, val, self.num_tweets, self.num_tweets+val))
        self.num_tweets += val

    def to_string(self) -> str:
        return "{}: {:,}".format(self.name, self.num_tweets)

class TweetDownloader(AppBase):
    msi:MySqlInterface
    tkws:TweetKeywords
    prompt_text_field:TextField
    response_text_field:TextField
    keyword_text_field:TextField
    start_date_field:DateEntryField
    end_date_field:DateEntryField
    cur_date_field:DateEntryField
    duration_field:DataField
    samples_field:DataField
    clamp_field:DataField
    corpus_size_field:DataField
    lowest_count_field:DataField
    highest_count_field:DataField
    percent_field:DataField
    option_checkboxes:Checkboxes
    keyword_data_list:List
    randomize:bool
    hour_offset:int


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword_data_list = []
        self.randomize = False
        self.hour_offset = 0 # offset from zulu
        print("TweetDownloader.init()")

    def setup_app(self):
        self.app_name = "TweetDownloader"
        self.app_version = "9.2.22"
        self.geom = (1000, 560)
        self.console_lines = 10
        self.text_width = 70

        self.tkws = TweetKeywords()
        self.msi = MySqlInterface(user_name ="root", db_name ="twitter_v2")
        if not self.tkws.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'BEARER_TOKEN_2'")

    def build_app_view(self, row:int, main_text_width:int, main_label_width:int) -> int:
        param_text_width = 20
        param_label_width = 15
        row += 1
        lf = tk.LabelFrame(self, text="Twitter")
        lf.grid(row=row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_twitter(lf, main_text_width, main_label_width)

        lf = tk.LabelFrame(self, text="Twitter Params")
        lf.grid(row=row, column=2, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_twitter_params(lf, param_text_width, param_label_width)

        self.end_date_field.set_date()
        day_delta = 3
        self.start_date_field.set_date(d = (datetime.utcnow() - timedelta(days=day_delta)))
        self.cur_date_field.set_date(d = (datetime.utcnow() - timedelta(days=day_delta)))
        self.duration_field.set_text(day_delta)

        return row+1

    def build_twitter(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.keyword_text_field = TextField(lf, row, 'Test Keyword(s)', text_width, height=10, label_width=label_width)
        ToolTip(self.keyword_text_field.tk_text,
                "List of terms to search.\nTerms can have spaces or be combined with OR:\nNorth Korea\nSouth Korea\nNorth Korea or South Korea")
        row = self.keyword_text_field.get_next_row()
        self.start_date_field = DateEntryField(lf, row, 'Start Date', text_width, label_width=label_width)
        row = self.start_date_field.get_next_row()
        self.end_date_field = DateEntryField(lf, row, 'End Date', text_width, label_width=label_width)
        row = self.end_date_field.get_next_row()
        self.duration_field = DataField(lf, row, 'Duration:', int(text_width/2), label_width=label_width)
        ToolTip(self.duration_field.tk_entry, "How many days in the pull\nCalculted from the start and stop dates")
        b = self.duration_field.add_button("set start", self.set_start_callback)
        ToolTip(b, "Reset the start date based on the end date and duration")
        b = self.duration_field.add_button("set end", self.set_end_callback)
        ToolTip(b, "Reset the end date based on the start date and duration")
        row = self.duration_field.get_next_row()
        buttons = Buttons(lf, row, "Collect:", label_width=label_width)
        b = buttons.add_button("Balanced", self.collect_balanced_callback)
        ToolTip(b, "Collect the same number (Samples/Clamp) of tweets per day for each item\nUses each day's smallest count")
        b = buttons.add_button("Percent", self.collect_percent_callback)
        ToolTip(b, "Collect a proportional (Percent) sample with\nan upper clamp (Samples/Clamp) per day for all terms\nMinimum of 10 samples per day")
        row = buttons.get_next_row()

        buttons = Buttons(lf, row, "Analytics:", label_width=label_width)
        b = buttons.add_button("Calc rates", self.calc_rates_callback)
        ToolTip(b, "Gets the rough number of tweets per day per term\n and prints to the Console window")
        b = buttons.add_button("Browser", self.launch_twitter_callback)
        ToolTip(b, "Open tabs in the default browser for each term over the time period")
        row = buttons.get_next_row()

    def build_twitter_params(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.samples_field = DataField(lf, row, 'Samples:', text_width, label_width=label_width)
        self.samples_field.set_text(TweetKeywords.max_tweets_per_sample)
        ToolTip(self.samples_field.tk_entry, "The sample size (10 - 500)")
        row = self.samples_field.get_next_row()

        self.clamp_field = DataField(lf, row, 'Clamp:', text_width, label_width=label_width)
        self.clamp_field.set_text(1000)
        ToolTip(self.clamp_field.tk_entry, "The max tweets to pull per day")
        row = self.clamp_field.get_next_row()

        self.percent_field = DataField(lf, row, 'Percent:', text_width, label_width=label_width)
        self.percent_field.set_text('10')
        ToolTip(self.percent_field.tk_entry, "The percent of the total tweets for an item")
        row = self.percent_field.get_next_row()

        self.option_checkboxes = Checkboxes(lf, row, "Options", label_width=label_width)
        cb = self.option_checkboxes.add_checkbox("Randomize", self.randomize_callback, dir=DIR.ROW)
        ToolTip(cb, "Randomly select the starting time for each day so that a full pull won't go into tomorrow")
        cb = self.option_checkboxes.add_checkbox("Stream to DB", self.implement_me, dir=DIR.ROW)
        ToolTip(cb, "Stream to DB: Default at this point. ")
        cb = self.option_checkboxes.add_checkbox("Stream to CSV", self.implement_me, dir=DIR.ROW)
        ToolTip(cb, "Stream to CSV: Not implemented")
        row = self.option_checkboxes.get_next_row()

        self.corpus_size_field = DataField(lf, row, 'Corpus Size:', text_width, label_width=label_width)
        self.corpus_size_field.set_text('2000')
        ToolTip(self.corpus_size_field.tk_entry, "The maximum number to download. if\nStops the pull before end date")
        row = self.corpus_size_field.get_next_row()

        self.lowest_count_field = DataField(lf, row, 'Lowest/Day:', text_width, label_width=label_width)
        self.lowest_count_field.set_text('0')
        ToolTip(self.lowest_count_field.tk_entry, "The item with fewest tweets. Set by Calc rates")
        row = self.lowest_count_field.get_next_row()

        self.highest_count_field = DataField(lf, row, 'Highest/Day:', text_width, label_width=label_width)
        self.highest_count_field.set_text('0')
        ToolTip(self.highest_count_field.tk_entry, "The item with fewest tweets. Set by Calc rates")
        row = self.highest_count_field.get_next_row()

        self.cur_date_field = DateEntryField(lf, row, 'Cur Date', text_width, label_width=label_width)
        ToolTip(self.cur_date_field.tk_entry, "The current date of the running pull")
        row = self.cur_date_field.get_next_row()

    def set_experiment_text(self, l:List):
        self.keyword_text_field.clear()
        pos = 0
        for s in reversed(l):
            self.keyword_text_field.add_text(s+"\n")
            pos += 1

    def save_experiment_text(self, filename:str):
        s = self.topic_text_field.get_text()
        with open(filename, mode="w", encoding="utf8") as f:
            f.write(s)

    def randomize_callback(self):
        self.randomize = not self.randomize
        # print("self.randomize = {}".format(self.randomize))

    def set_start_callback(self):
        duration = int(self.duration_field.get_text())
        end_dt = self.end_date_field.get_date()
        start_dt = end_dt - timedelta(days= duration)
        self.start_date_field.set_date(start_dt)
        self.cur_date_field.set_date(start_dt)

    def set_end_callback(self):
        duration = int(self.duration_field.get_text())
        start_dt = self.start_date_field.get_date()
        end_dt = start_dt + timedelta(days = duration)
        self.end_date_field.set_date(end_dt)

    # TODO: Add condition that exits when corpus size is reached
    def collect_percent_callback(self):
        date_fmt = "%B %d, %Y (%H:%M:%S)"
        percent = self.percent_field.get_as_int()
        clamp = self.clamp_field.get_as_int()
        # get the keywords
        key_list = self.keyword_text_field.get_list("\n")
        # set up the counters for corpus size
        corpus_size_dict = {}
        for s in key_list:
            corpus_size_dict[s] = KeywordData(s)

        # get the entire date range
        cur_dt = self.start_date_field.get_date()
        end_dt = self.end_date_field.get_date()

        # save this experiment to the database
        sql = "insert into table_experiment (name, date, sample_start, sample_end, keywords) values (%s, %s, %s, %s, %s)"
        values = (self.experiment_field.get_text(), datetime.now(), cur_dt, end_dt, ", ".join(key_list))
        experiment_id = -1
        experiment_id = self.msi.write_sql_values_get_row(sql, values)

        # starting with the start date, step towards the end date one day at a time
        while cur_dt < end_dt:
            # Get the number of tweets for each keyword for today. From cur_dt to max_end is 24 hours
            # from 0 Zulu
            max_end = cur_dt + timedelta(days=1)
            print("\n-------------------------{}-------------------------".format(cur_dt.strftime(date_fmt)))

            # first, get the counts for each keyword for this day
            self.keyword_data_list = []
            for s in key_list:
                print("\n-------------------------------\n{}".format(s))
                corpus_kd:KeywordData = corpus_size_dict[s]
                corpus_size = self.corpus_size_field.get_as_int()
                if corpus_kd.num_tweets > corpus_size:
                    print("collect_percent_callback({}):  already has more than {} tweets. Skipping...".format(s, corpus_size))
                    continue
                count = self.tkws.get_keywords_per_day(s, cur_dt)
                print("collect_percent_callback() count = {:,}".format(count))

                scaled = count * percent/100
                print("collect_percent_callback() scaled = {:,}".format(scaled))

                tweets_to_download = int(min(scaled, clamp))
                tweets_to_download = max(TweetKeywords.min_tweets_per_sample, tweets_to_download)
                print("collect_percent_callback() tweets_to_download = {:,}".format(tweets_to_download))

                remaining = corpus_size - corpus_kd.num_tweets
                tweets_to_download = min(remaining, tweets_to_download)
                print("collect_percent_callback() tweets_to_download (adjusted for corpus remaining: {:,}) = {:,}".format(remaining, tweets_to_download))

                tk:TweetKeyword = TweetKeyword(s)
                ratio = tweets_to_download / count
                day_offset = random.random() * (1.0 - 2*ratio)
                cur_start = cur_dt + timedelta(days=day_offset)
                cur_end = max_end #cur_start + timedelta(days=ratio)
                tweets_per_sample = min(tweets_to_download, TweetKeywords.max_tweets_per_sample)
                print("collect_percent_callback() tweets_per_sample = {:,} ".format(tweets_per_sample))
                self.tkws.get_keywords(tk, cur_start, end_dt=cur_end, tweets_per_sample=tweets_per_sample,
                                       tweets_to_download=tweets_to_download, msi=self.msi, experiment_id=experiment_id)
                corpus_kd:KeywordData = corpus_size_dict[s]
                corpus_kd.add_to_num_tweets(tk.num_entries)

            self.cur_date_field.set_date(cur_dt)
            self.cur_date_field.update()
            # next day
            cur_dt += timedelta(days=1)
        print("collect_percent_callback() - done")


    # Collect the same number of tweets for each keyword over the sample duration
    # TODO: Add condition that exits when corpus size is reached
    def collect_balanced_callback(self):
        date_fmt = "%B %d, %Y (%H:%M:%S)"

        # get the keywords
        key_list = self.keyword_text_field.get_list("\n")
        # set up the counters for corpus size
        corpus_size_dict = {}
        for s in key_list:
            corpus_size_dict[s] = KeywordData(s)

        # get the entire date range
        cur_dt = self.start_date_field.get_date()
        end_dt = self.end_date_field.get_date()

        # save this experiment to the database
        sql = "insert into table_experiment (name, date, sample_start, sample_end, keywords) values (%s, %s, %s, %s, %s)"
        values = (self.experiment_field.get_text(), datetime.now(), cur_dt, end_dt, ", ".join(key_list))
        experiment_id = self.msi.write_sql_values_get_row(sql, values)

        # starting with the start date, step towards the end date one day at a time
        while cur_dt < end_dt:
            # Get the number of tweets for each keyword for today. From cur_dt to max_end is 24 hours
            # from 0 Zulu
            max_end = cur_dt + timedelta(days=1)
            print("\n{}".format(cur_dt.strftime(date_fmt)))

            # first, get the counts for each keyword for this day
            self.keyword_data_list = []
            for s in key_list:
                count = self.tkws.get_keywords_per_day(s, cur_dt)
                self.keyword_data_list.append(KeywordData(s, count))
            self.keyword_data_list.sort(key=lambda kd:kd.num_tweets)

            #get the keyword with the lowest number of tweets
            kd:KeywordData
            min_kd:KeywordData = self.keyword_data_list[0]

            # If the lowest number of tweets is less than max_tweets_per_sample,
            # then set max_tweets_per_sample to that value, or the minimum allowed
            # by the Twitter API
            one_random_sample = self.randomize
            # get the max number of samples that we want to get per day
            max_tweets_per_sample = self.samples_field.get_as_int()
            if min_kd.num_tweets <= max_tweets_per_sample:
                max_tweets_per_sample = max(TweetKeywords.min_tweets_per_sample, min_kd.num_tweets)
                one_random_sample = True

            # For each keyword in the sorted list
            for kd in self.keyword_data_list:
                tk:TweetKeyword = TweetKeyword(kd.name)

                corpus_kd:KeywordData = corpus_size_dict[kd.name]
                corpus_size = self.corpus_size_field.get_as_int()
                if corpus_kd.num_tweets > corpus_size:
                    print("collect_balanced_callback(): {} already has more than {} tweets. Skipping...".format(kd.name, corpus_size))
                    continue

                # The tweets per sample has to be >= the Twitter API
                tweets_per_sample = min(self.tkws.max_tweets_per_sample, kd.num_tweets)

                # The sample size is within user specs
                if kd.num_tweets <= max_tweets_per_sample:
                    # get the dates we're going to collect
                    cur_start = cur_dt
                    cur_end = max_end


                    #show the date we are collecting for
                    print("\n{} collecting all of {:,} tweets".format(kd.name, kd.num_tweets))
                    print("\tcollecting all from {} to {}".format(cur_start.strftime(date_fmt), cur_end.strftime(date_fmt)))

                    # collect all the tweets for this keyword.
                    self.tkws.get_keywords(tk, cur_start, end_dt=cur_end, tweets_per_sample=tweets_per_sample,
                                           tweets_to_download=kd.num_tweets, msi=self.msi, experiment_id=experiment_id)

                # if there are more tweets than the user spec
                else:
                    if one_random_sample:
                        # Make one random sample in the day
                        ratio = min_kd.num_tweets / kd.num_tweets
                        if self.randomize:
                            ratio = max_tweets_per_sample / kd.num_tweets
                        day_offset = random.random() * (1.0 - 2*ratio)
                        cur_start = cur_dt + timedelta(days=day_offset)
                        cur_end = max_end #cur_start + timedelta(days=ratio)
                        print("{}: Randomly choosing {}/{:,} from {} to {}".format(kd.name, max_tweets_per_sample, kd.num_tweets, cur_start.strftime(date_fmt), cur_end.strftime(date_fmt)))
                        self.tkws.get_keywords(tk, cur_start, end_dt=cur_end, tweets_per_sample=tweets_per_sample,
                                               tweets_to_download=max_tweets_per_sample, msi=self.msi, experiment_id=experiment_id)
                        total_downloaded = tk.get_entries()

                    else:
                        total_downloaded = 0
                        # Make several samples across the day
                        day_frac = max_tweets_per_sample / min_kd.num_tweets

                        #show the date we are collecting for
                        print("\n{} subsampling {:,} of {:,} tweets".format(kd.name, min_kd.num_tweets, kd.num_tweets))

                        total_frac = 0
                        count = 0
                        while total_frac < 1.0:
                            sample_size = min(TweetKeywords.max_tweets_per_sample, min_kd.num_tweets - (count * TweetKeywords.max_tweets_per_sample))
                            # get the dates we're going to collect
                            cur_start = cur_dt + timedelta(days=(count * day_frac))
                            total_frac = min(1.0, (count+1) * day_frac)
                            cur_end = cur_dt + timedelta(days=total_frac)
                            print("\tsubsampling {} from {} to {}".format(sample_size, cur_start.strftime(date_fmt), cur_end.strftime(date_fmt)))
                            self.tkws.get_keywords(tk, cur_start, end_dt=cur_end, tweets_per_sample=tweets_per_sample,
                                                   tweets_to_download=kd.num_tweets, msi=self.msi, experiment_id=experiment_id)
                            total_downloaded += tk.get_entries()
                            print("\t[{}]: got {} out of a max of {}".format(kd.name, total_downloaded, kd.num_tweets))
                            if total_downloaded > kd.num_tweets:
                                print("\t[{}]: got {} out of a max of {} for the day, breaking loop".format(kd.name, total_downloaded, kd.num_tweets))
                                break
                            count += 1
                    # we may not have pulled as many tweets as we thought, so change the amount for the next as needed
                    old_mkd = min_kd.num_tweets
                    min_kd.num_tweets = min(min_kd.num_tweets, total_downloaded)
                    print("max_tweets_per_sample set from {} to {}".format(old_mkd, min_kd.num_tweets))

                    print("collect_balanced_callback() - done")

                # add to the full counts
                corpus_kd:KeywordData = corpus_size_dict[kd.name]
                corpus_kd.add_to_num_tweets(tk.num_entries)

            self.cur_date_field.set_date(cur_dt)
            self.cur_date_field.update()
            # next day
            cur_dt += timedelta(days=1)


        print("collect_individual_callback(): done")


    def calc_rates_callback(self):
        corpus_size = int(self.corpus_size_field.get_text())
        key_list = self.keyword_text_field.get_list("\n")
        start_dt = self.start_date_field.get_date()
        i = 0
        highest = KeywordData("unset", 0)
        lowest = KeywordData("unset", 0)
        self.dp.clear()
        self.keyword_data_list = []
        for s in key_list:
            percent = self.percent_field.get_as_int()/100.0
            count = int(self.tkws.get_keywords_per_day(s, start_dt) * percent)
            if count == 0:
                self.dp.dprint("{}: {:,} SKIPPING".format(s, count))
                continue
            self.keyword_data_list.append(KeywordData(s, count))
            if i == 0:
                lowest.reset(s, count)
                highest.reset(s, count)
            else:
                if count < lowest.num_tweets:
                    lowest.reset(s, count)
                elif count > highest.num_tweets:
                    highest.reset(s, count)
            self.dp.dprint("[{}]{:.1f}%: {:,} keywords/day = {:.1f} days for {}k ".format(s, percent*100, count, corpus_size/count+1, corpus_size/1000))
            i += 1
        self.highest_count_field.set_text(highest.to_string())
        self.lowest_count_field.set_text(lowest.to_string())

        # sort the list from lowest to highest
        kd:KeywordData
        self.keyword_data_list.sort(key=lambda kd:kd.num_tweets)
        for kd in self.keyword_data_list:
            print(kd.to_string())

    def launch_twitter_callback(self):
        # single word
        key_list = self.keyword_text_field.get_list("\n")
        start_dt = self.start_date_field.get_date()
        end_dt = self.end_date_field.get_date()
        self.log_action("Launch_twitter", {"twitter_start": start_dt.strftime("%Y-%m-%d"), "twitter_end":end_dt.strftime("%Y-%m-%d"), "terms":" ".join(key_list)})
        self.tkws.launch_twitter(key_list, start_dt, end_dt)
        # webbrowser.open('https://twitter.com/search?q=chinavirus%20until%3A2020-02-01%20since%3A2019-12-01&src=typed_query')
        # webbrowser.open('https://twitter.com/search?q=%22china%20virus%22%20until%3A2020-02-01%20since%3A2019-12-01&src=typed_query')

    def set_time_sample_callback(self, event:tk.Event = None):
        sample_str = self.sample_list.get_selected()
        self.sample_list.set_label("Sample\n({})".format(sample_str))

    def clean_list_text(self, s:str) -> str:
        """
        Convenience method to clean up list-style text. Useful for a good chunk of the GPT-3 responses for
        the style of prompt that I've been using
        :param s: The string to clean up
        :return: The cleaned-up string
        """
        lines = s.split("\n")
        line:str
        par =""
        for line in lines:
            s = line.strip()
            if s != "":
                par = "{}\n{}".format(par, s)
        return par.strip()


def main():
    app = TweetDownloader()
    app.mainloop()

if __name__ == "__main__":
    main()