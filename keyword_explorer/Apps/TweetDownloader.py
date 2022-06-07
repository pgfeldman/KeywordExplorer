import getpass
import tkinter as tk
import tkinter.messagebox as message
from datetime import datetime, timedelta
from tkinter import filedialog

import pandas as pd

from keyword_explorer.Apps.AppBase import AppBase
from keyword_explorer.TwitterV2.TweetKeywords import TweetKeywords
from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.Checkboxes import Checkboxes, DIR
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.DateEntryField import DateEntryField
from keyword_explorer.tkUtils.ListField import ListField
from keyword_explorer.tkUtils.TextField import TextField

from typing import Dict

class TweetDownloader(AppBase):
    tkey:TweetKeywords
    prompt_text_field:TextField
    response_text_field:TextField
    keyword_text_field:TextField
    start_date_field:DateEntryField
    end_date_field:DateEntryField
    token_list:ListField
    engine_list:ListField
    sample_list:ListField
    samples_field:DataField
    sample_mult_field:DataField
    option_checkboxes:Checkboxes


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.totals_dict = {}
        print("TweetDownloader")

    def setup_app(self):
        self.app_name = "TweetDownloader"
        self.app_version = "5.7.22"
        self.geom = (850, 440)

        self.tkey = TweetKeywords()
        if not self.tkey.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'BEARER_TOKEN_2'")

    def build_app_view(self, row:int, main_text_width:int, main_label_width:int) -> int:
        param_text_width = 15
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
        row = self.keyword_text_field.get_next_row()
        self.start_date_field = DateEntryField(lf, row, 'Start Date', text_width, label_width=label_width)
        row = self.start_date_field.get_next_row()
        self.end_date_field = DateEntryField(lf, row, 'End Date', text_width, label_width=label_width)
        row = self.end_date_field.get_next_row()
        buttons = Buttons(lf, row, "Actions", label_width=label_width)
        buttons.add_button("Individual", self.implement_me())
        buttons.add_button("OR everything!", self.implement_me())
        buttons.add_button("Launch Twitter", self.launch_twitter_callback)
        row = buttons.get_next_row()

    def build_twitter_params(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.sample_list = ListField(lf, row, "Sample", width=text_width, label_width=label_width, static_list=True)
        self.sample_list.set_text(text='hour, day, week, month')
        self.sample_list.set_callback(self.set_time_sample_callback)
        self.set_time_sample_callback()
        row = self.sample_list.get_next_row()

        self.samples_field = DataField(lf, row, 'Samples (10 - 500):', text_width, label_width=label_width)
        self.samples_field.set_text('500')
        row = self.samples_field.get_next_row()

        self.sample_mult_field = DataField(lf, row, 'Sample Multiple:', text_width, label_width=label_width)
        self.sample_mult_field.set_text('1')
        row = self.sample_mult_field.get_next_row()

        self.option_checkboxes = Checkboxes(lf, row, "Options")
        self.option_checkboxes.add_checkbox("Randomize", self.implement_me, dir=DIR.ROW)
        self.option_checkboxes.add_checkbox("Save to DB", self.implement_me, dir=DIR.ROW)
        self.option_checkboxes.add_checkbox("Save to CSV", self.implement_me, dir=DIR.ROW)
        row = self.option_checkboxes.get_next_row()



    def launch_twitter_callback(self):
        # single word
        key_list = self.keyword_text_field.get_list("\n")
        start_dt = self.start_date_field.get_date()
        end_dt = self.end_date_field.get_date()
        self.log_action("Launch_twitter", {"twitter_start": start_dt.strftime("%Y-%m-%d"), "twitter_end":end_dt.strftime("%Y-%m-%d"), "terms":" ".join(key_list)})
        self.tkey.launch_twitter(key_list, start_dt, end_dt)
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