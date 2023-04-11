import getpass
import tkinter as tk
import tkinter.messagebox as message
from datetime import datetime, timedelta
from tkinter import filedialog

import pandas as pd

from keyword_explorer.Apps.AppBase import AppBase
from keyword_explorer.TwitterV2.TwitterV2Counts import TwitterV2Counts, TwitterV2Count
from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.ToolTip import ToolTip
from keyword_explorer.tkUtils.DateEntryField import DateEntryField
from keyword_explorer.tkUtils.ListField import ListField
from keyword_explorer.tkUtils.TextField import TextField
from keyword_explorer.tkUtils.DataField import DataField

from typing import List

class TweetCountExplorer(AppBase):
    tvc:TwitterV2Counts
    prompt_text_field:TextField
    response_text_field:TextField
    keyword_text_field:TextField
    start_date_field:DateEntryField
    end_date_field:DateEntryField
    token_list:ListField
    engine_list:ListField
    sample_list:ListField
    query_options_field:DataField
    action_buttons:Buttons


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.totals_dict = {}
        print("TweetCountExplorer")

    def setup_app(self):
        self.app_name = "TweetCountExplorer"
        self.app_version = "11.15.22"
        self.geom = (900, 440)

        self.tvc = TwitterV2Counts()
        if not self.tvc.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'BEARER_TOKEN_2'")

    def build_app_view(self, row:int, main_text_width:int, main_label_width:int) -> int:
        param_text_width = 22
        param_label_width = 15
        row += 1
        lf = tk.LabelFrame(self, text="Twitter")
        lf.grid(row=row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_twitter(lf, main_text_width, main_label_width)

        lf = tk.LabelFrame(self, text="Twitter Params")
        lf.grid(row=row, column=2, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_twitter_params(lf, param_text_width, param_label_width)

        self.end_date_field.set_date()
        self.start_date_field.set_date(d = (datetime.utcnow() - timedelta(days=10)))

        return row+1

    def build_twitter(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.keyword_text_field = TextField(lf, row, 'Test Keyword(s)', text_width, height=10, label_width=label_width)
        ToolTip(self.keyword_text_field.tk_text,
            "List of terms to search.\nTerms can have spaces or be combined with OR:\nNorth Korea\nSouth Korea\nNorth Korea OR South Korea")
        row = self.keyword_text_field.get_next_row()
        self.start_date_field = DateEntryField(lf, row, 'Start Date', text_width, label_width=label_width)
        row = self.start_date_field.get_next_row()
        self.end_date_field = DateEntryField(lf, row, 'End Date', text_width, label_width=label_width)
        row = self.end_date_field.get_next_row()
        self.action_buttons = Buttons(lf, row, "Actions", label_width=label_width)
        b = self.action_buttons.add_button("Clear", self.clear_counts_callbacks, width=-1)
        ToolTip(b, "Clears any old data from the plot")
        b = self.action_buttons.add_button("Test Keyword", self.test_keyword_callback, width=-1)
        ToolTip(b, "Query Twitter for each keyword and plot")
        b = self.action_buttons.add_button("Plot", self.plot_counts_callback, width=-1)
        ToolTip(b, "Plot the current data")
        b = self.action_buttons.add_button("Save", self.save_callback, width=-1)
        ToolTip(b, "Save the results as an xlsx file")
        b = self.action_buttons.add_button("Launch Twitter", self.launch_twitter_callback, width=-1)
        ToolTip(b, "Open tabs in the default browser for each term over the time period")
        row = self.action_buttons.get_next_row()

    def build_twitter_params(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.sample_list = ListField(lf, row, "Sample", width=text_width, label_width=label_width, static_list=True)
        self.sample_list.set_text(text='day, week, month')
        self.sample_list.set_callback(self.set_time_sample_callback)
        ToolTip(self.sample_list.tk_list, "The sampling period\nWeek and month are subsamples")
        self.set_time_sample_callback()
        row = self.sample_list.get_next_row()

        self.query_options_field = DataField(lf, row, 'Query Options', text_width, label_width=label_width)
        self.query_options_field.set_text("lang:en -is:retweet")
        ToolTip(self.query_options_field.tk_entry, "TwitterV2 args. Default is English (en), and no retweets\nMore info is available here:\ndeveloper.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query")
        row = self.query_options_field.get_next_row()

    def launch_twitter_callback(self):
        # single word
        key_list = self.keyword_text_field.get_list("\n")
        start_dt = self.start_date_field.get_date()
        end_dt = self.end_date_field.get_date()
        self.log_action("Launch_twitter", {"twitter_start": start_dt.strftime("%Y-%m-%d"), "twitter_end":end_dt.strftime("%Y-%m-%d"), "terms":" ".join(key_list)})
        self.tvc.launch_twitter(key_list, start_dt, end_dt)
        # webbrowser.open('https://twitter.com/search?q=chinavirus%20until%3A2020-02-01%20since%3A2019-12-01&src=typed_query')
        # webbrowser.open('https://twitter.com/search?q=%22china%20virus%22%20until%3A2020-02-01%20since%3A2019-12-01&src=typed_query')

    def set_time_sample_callback(self, event:tk.Event = None):
        sample_str = self.sample_list.get_selected()
        self.sample_list.set_label("Sample\n({})".format(sample_str))

    def test_keyword_callback(self):
        key_list = self.keyword_text_field.get_list("\n")
        print(key_list)
        start_dt = self.start_date_field.get_date()
        end_dt = self.end_date_field.get_date()

        clean_list = []
        keyword:str
        for keyword in key_list:
            if len(keyword) > 2:
                clean_list.append(keyword.strip())

        if len(clean_list) == 0:
            message.showwarning("Keyword(s) too short",
                                "Please enter something longer than [{}] text area".format(key_list))
            return
        tweet_options = self.query_options_field.get_text()
        granularity = self.sample_list.get_selected()
        log_dict = {"granularity":granularity, "twitter_start": start_dt.strftime("%Y-%m-%d"), "twitter_end":end_dt.strftime("%Y-%m-%d")}
        for keyword in clean_list:
            if granularity == 'day':
                self.tvc.get_counts(keyword, start_dt, end_time=end_dt, granularity=granularity, tweet_options=tweet_options)
                print("testing keyword {} between {} and {} - granularity = {}".format(keyword, start_dt, end_dt, granularity))
            elif granularity == 'week':
                self.tvc.get_sampled_counts(keyword, start_dt, end_time=end_dt, skip_days=7, tweet_options=tweet_options)
                print("testing keyword {} between {} and {} - skip_days = {}".format(keyword, start_dt, end_dt, 7))
            elif granularity == 'month':
                self.tvc.get_sampled_counts(keyword, start_dt, end_time=end_dt, skip_days=30, tweet_options=tweet_options)
                print("testing keyword {} between {} and {} - skip_days = {}".format(keyword, start_dt, end_dt, 30))
            else:
                self.dp.dprint("test_keyword_callback() unable to handle granularity = {}".format(granularity))
                return

            tvc:TwitterV2Count
            for tvc in self.tvc.count_list:
                print(tvc.to_string())
        for k, v in self.tvc.totals_dict.items():
            log_dict[k] = v
        self.log_action("test_keyword", log_dict)
        self.tvc.plot()

    def set_experiment_text(self, l:List):
        self.keyword_text_field.clear()
        pos = 0
        for s in reversed(l):
            self.keyword_text_field.add_text(s+"\n")
            pos += 1

    def save_experiment_text(self, filename:str):
        s = self.keyword_text_field.get_text()
        with open(filename, mode="w", encoding="utf8") as f:
            f.write(s)

    def clear_counts_callbacks(self):
        self.tvc.reset()

    def plot_counts_callback(self):
        self.tvc.plot()

    def save_callback(self):
        default = "{} {}.xlsx".format(self.experiment_field.get_text(), datetime.now().strftime("%B_%d_%Y_(%H_%M_%S)"))
        filename = filedialog.asksaveasfilename(filetypes=(("Excel files", "*.xlsx"),("All Files", "*.*")), title="Save Excel File", initialfile=default)
        if filename:
            print("saving to {}".format(filename))
            df1 = self.get_description_df()
            df2 = self.tvc.to_dataframe()
            with pd.ExcelWriter(filename) as writer:
                df1.to_excel(writer, sheet_name='Experiment')
                df2.to_excel(writer, sheet_name='Results')
                writer.save()
            self.log_action("save", {"filename":filename})

    def get_description_df(self) -> pd.DataFrame:
        now = datetime.now()
        now_str = now.strftime("%B_%d_%Y_(%H:%M:%S)")
        sample_str = self.sample_list.get_selected()

        description_dict = {'name':getpass.getuser(), 'date':now_str, 'sampling':sample_str}
        df = pd.DataFrame.from_dict(description_dict, orient='index', columns=['Value'])
        return df

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
    app = TweetCountExplorer()
    app.mainloop()

if __name__ == "__main__":
    main()