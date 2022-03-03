import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as message
from tkinter import filedialog
import inspect
import re
import getpass
import webbrowser
import urllib
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Any, Union, Dict


from keyword_explorer.TwitterV2.TwitterV2Counts import TwitterV2Counts, TwitterV2Count

from keyword_explorer.tkUtils.TextField import TextField
from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.ConsoleDprint import ConsoleDprint
from keyword_explorer.tkUtils.DateEntryField import DateEntryField
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.ListField import ListField

class TweetCountExplorer(tk.Tk):
    main_console:tk.Text
    dp:ConsoleDprint
    tvc:TwitterV2Counts
    prompt_text_field:TextField
    response_text_field:TextField
    keyword_text_field:TextField
    start_date_field:DateEntryField
    end_date_field:DateEntryField
    regex_field:DataField
    experiment_field:DataField
    token_list:ListField
    engine_list:ListField
    sample_list:ListField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("KeywordExplorer")
        self.dp = ConsoleDprint()
        self.tvc = TwitterV2Counts()

        self.title("TweetCountExplorer (v 3.2.22)")
        self.geometry("850x425")
        self.resizable(width=True, height=False)
        self.build_view()

        if not self.tvc.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'BEARER_TOKEN_2'")

    def build_view(self):
        print("build_view")
        main_text_width = 53
        main_label_width = 15
        param_text_width = 15
        param_label_width = 15

        self.experiment_field = DataField(self, 0, "Experiment name:", 40, label_width=20)
        self.experiment_field.set_text(getpass.getuser())

        lf = tk.LabelFrame(self, text="Twitter")
        lf.grid(row=1, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_twitter(lf, main_text_width, main_label_width)

        lf = tk.LabelFrame(self, text="Twitter Params")
        lf.grid(row=1, column=2, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_twitter_params(lf, param_text_width, param_label_width)

        self.dp.create_tk_console(self, row=2, height=5, char_width=main_text_width+main_label_width, set_console=True)
        self.dp.dprint("build_view()")
        self.end_date_field.set_date()
        self.start_date_field.set_date(d = (datetime.utcnow() - timedelta(days=10)))

    def build_twitter(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.keyword_text_field = TextField(lf, row, 'Test Keyword(s)', text_width, height=10, label_width=label_width)
        row = self.keyword_text_field.get_next_row()
        self.start_date_field = DateEntryField(lf, row, 'Start Date', text_width, label_width=label_width)
        row = self.start_date_field.get_next_row()
        self.end_date_field = DateEntryField(lf, row, 'End Date', text_width, label_width=label_width)
        row = self.end_date_field.get_next_row()
        buttons = Buttons(lf, row, "Actions", label_width=label_width)
        buttons.add_button("Clear", self.clear_counts_callbacks)
        buttons.add_button("Test Keyword", self.test_keyword_callback)
        buttons.add_button("Plot", self.plot_counts_callback)
        buttons.add_button("Save", self.save_callback)
        buttons.add_button("Launch Twitter", self.launch_twitter_callback)
        row = buttons.get_next_row()

    def build_twitter_params(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.sample_list = ListField(lf, row, "Sample", width=text_width, label_width=label_width, static_list=True)
        self.sample_list.set_text(text='day, week, month')
        self.sample_list.set_callback(self.set_time_sample_callback)
        self.set_time_sample_callback()
        row = self.sample_list.get_next_row()

    def launch_twitter_callback(self):
        # single word
        key_list = self.keyword_text_field.get_list("\n")
        start_dt = self.start_date_field.get_date()
        end_dt = self.end_date_field.get_date()
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

        for keyword in key_list:
            if len(keyword) < 3:
                message.showwarning("Keyword too short",
                                    "Please enter something longer than [{}] text area".format(keyword))
                return

        granularity = self.sample_list.get_selected()
        for keyword in key_list:
            if granularity == 'day':
                self.tvc.get_counts(keyword, start_dt, end_time=end_dt, granularity=granularity)
                print("testing keyword {} between {} and {} - granularity = {}".format(keyword, start_dt, end_dt, granularity))
            elif granularity == 'week':
                self.tvc.get_sampled_counts(keyword, start_dt, end_time=end_dt, skip_days=7)
                print("testing keyword {} between {} and {} - skip_days = {}".format(keyword, start_dt, end_dt, 7))
            elif granularity == 'month':
                self.tvc.get_sampled_counts(keyword, start_dt, end_time=end_dt, skip_days=30)
                print("testing keyword {} between {} and {} - skip_days = {}".format(keyword, start_dt, end_dt, 30))
            else:
                self.dp.dprint("test_keyword_callback() unable to handle granularity = {}".format(granularity))
                return

            tvc:TwitterV2Count
            for tvc in self.tvc.count_list:
                print(tvc.to_string())
        self.tvc.plot()

    def clear_counts_callbacks(self):
        self.tvc.reset()

    def plot_counts_callback(self):
        self.tvc.plot()

    def save_callback(self):
        default = "{} {}.xlsx".format(self.experiment_field.get_text(), datetime.now().strftime("%B_%d_%Y_(%H_%M_%S)"))
        filename = filedialog.asksaveasfilename(filetypes=(("Excel files", "*.xlsx"),("All Files", "*.*")), title="Save Excel File", initialfile=default)
        if filename:
            print("saving to {}".format(filename))
            df1 = self.get_description_df(self.prompt_text_field.get_text(), self.response_text_field.get_text())
            df2 = self.tvc.to_dataframe()
            with pd.ExcelWriter(filename) as writer:
                df1.to_excel(writer, sheet_name='Experiment')
                df2.to_excel(writer, sheet_name='Results')
                writer.save()

    def get_description_df(self, probe:str, response:str) -> pd.DataFrame:
        now = datetime.now()
        now_str = now.strftime("%B_%d_%Y_(%H:%M:%S)")
        sample_str = self.sample_list.get_selected()

        description_dict = {'name':getpass.getuser(), 'date':now_str, 'probe':probe, 'response':response, 'sampling':sample_str}
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

    def terminate(self):
        """
        The callback called when clicking the exit button
        :return:
        """
        print("terminating")
        self.destroy()

    def implement_me(self, event:tk.Event = None):
        """
        A callback to point to when you you don't have a method ready. Prints "implement me!" to the output and
        an abbreviated version of the call stack to the console
        :return:
        """
        #self.dprint("Implement me!")
        self.dp.dprint("Implement me! (see console for call stack)")
        fi:inspect.FrameInfo
        count = 0
        self.dp.dprint("\nImplement me!")
        for fi in inspect.stack():
            filename = re.split(r"(/)|(\\)", fi.filename)
            print("Call stack[{}] = {}() (line {} in {})".format(count, fi.function, fi.lineno, filename[-1]))

def main():
    app = TweetCountExplorer()
    app.mainloop()

if __name__ == "__main__":
    main()