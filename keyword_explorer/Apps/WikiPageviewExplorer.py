import getpass
import os
import tkinter as tk
import tkinter.messagebox as message
import webbrowser
from datetime import datetime, timedelta
from tkinter import filedialog
from typing import List

import matplotlib.pyplot as plt
import pandas as pd

import keyword_explorer.utils.wikipedia_search as ws
from keyword_explorer.Apps.AppBase import AppBase
from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.ToolTip import ToolTip
from keyword_explorer.tkUtils.DateEntryField import DateEntryField
from keyword_explorer.tkUtils.ListField import ListField
from keyword_explorer.tkUtils.TextField import TextField


class WikiPageviewExplorer(AppBase):
    topic_text_field:TextField
    response_text_field:TextField
    wiki_pages_text_field:TextField
    start_date_field:DateEntryField
    end_date_field:DateEntryField
    sample_list:ListField
    multi_count_list:List
    topic_action_buttons:Buttons
    views_action_buttons:Buttons
    totals_dict:dict
    user_agent:str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("WikiPageviewExplorer.md")

    def setup_app(self):
        self.app_name = "WikiPageviewExplorer.md"
        self.app_version = "6.01.23"
        self.geom = (850, 700)

        self.multi_count_list = []
        self.totals_dict = {}
        self.user_agent = os.environ.get("USER_AGENT")
        if self.user_agent == None:
            message.showwarning("Key Error", "Could not find Environment key 'USER_AGENT'")


    def build_app_view(self, row:int, main_text_width:int, main_label_width:int) -> int:
        param_text_width = 15
        param_label_width = 15
        row += 1

        lf = tk.LabelFrame(self, text="Topic Search")
        lf.grid(row=row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_topic_search(lf, main_text_width, main_label_width)
        row += 1

        lf = tk.LabelFrame(self, text="Page Views")
        lf.grid(row=row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_page_views(lf, main_text_width, main_label_width)

        lf = tk.LabelFrame(self, text="Page View Params")
        lf.grid(row=row, column=2, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_page_view_params(lf, param_text_width, param_label_width)

        self.end_date_field.set_date()
        self.start_date_field.set_date(d = (datetime.utcnow() - timedelta(days=10)))

        return row + 1

    def build_topic_search(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.topic_text_field = TextField(lf, row, "Topic", text_width, height=5, label_width=label_width)
        self.topic_text_field.set_text("simpson characters\npinky and the brain")
        ToolTip(self.topic_text_field.tk_text, "List of possible Wikipedia topics")
        row = self.topic_text_field.get_next_row()
        self.response_text_field = TextField(lf, row, 'Response', text_width, height=10, label_width=label_width)
        ToolTip(self.response_text_field.tk_text, "List of best matches in English Wikipedia\nSelect the desired results to examine and\nclick 'Copy Selected'")
        row = self.response_text_field.get_next_row()
        self.topic_action_buttons = Buttons(lf, row, "Actions", label_width=label_width)
        b = self.topic_action_buttons.add_button("Search", self.search_wiki_callback, width=-1)
        ToolTip(b, "Search for best matches in English Wikipedia")
        b = self.topic_action_buttons.add_button("Copy Selected", self.copy_selected_callback, width=-1)
        ToolTip(b, "Copy selected responses to 'Pages' below for views")
        row = self.topic_action_buttons.get_next_row()

    def build_page_views(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.wiki_pages_text_field = TextField(lf, row, 'Pages', text_width, height=7, label_width=label_width)
        ToolTip(self.wiki_pages_text_field.tk_text, "The list of topics to get page views for")
        row = self.wiki_pages_text_field.get_next_row()
        self.start_date_field = DateEntryField(lf, row, 'Start Date', text_width, label_width=label_width)
        row = self.start_date_field.get_next_row()
        self.end_date_field = DateEntryField(lf, row, 'End Date', text_width, label_width=label_width)
        row = self.end_date_field.get_next_row()
        self.views_action_buttons = Buttons(lf, row, "Actions", label_width=label_width)
        b = self.views_action_buttons.add_button("Clear", self.clear_pageviews_callback)
        ToolTip(b, "Clears the topics from the Views text area")
        b = self.views_action_buttons.add_button("Test Pages", self.test_pages_callback, width=-1)
        ToolTip(b, "Query page views between Start Date and End Date and plot results")
        b = self.views_action_buttons.add_button("Plot", self.plot_callback, width=-1)
        ToolTip(b, "Plot page views")
        b = self.views_action_buttons.add_button("Save", self.save_callback, width=-1)
        ToolTip(b, "Save page views to Excel file")
        b = self.views_action_buttons.add_button("Show Pages", self.show_pages_callback, width=-1)
        ToolTip(b, "Launch each Wikipedia page as a separate tab in the default browser")
        row = self.views_action_buttons.get_next_row()
        b = self.views_action_buttons.add_button("Save Text", self.save_page_text_callback, width=-1)
        ToolTip(b, "Save each Wikipedia page as a separate text file in the specified directory")
        row = self.views_action_buttons.get_next_row()

    def build_page_view_params(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.sample_list = ListField(lf, row, "Sample", width=text_width, label_width=label_width, static_list=True)
        self.sample_list.set_text(text='daily, monthly')
        self.sample_list.set_callback(self.set_time_sample_callback)
        self.set_time_sample_callback()
        ToolTip(self.sample_list.tk_list, "Sampling period")
        row = self.sample_list.get_next_row()

    def set_experiment_text(self, l:List):
        self.topic_text_field.clear()
        pos = 0
        for s in reversed(l):
            self.topic_text_field.add_text(s+"\n")
            pos += 1

    def save_experiment_text(self, filename:str):
        s = self.topic_text_field.get_text()
        with open(filename, mode="w", encoding="utf8") as f:
            f.write(s)

    def copy_selected_callback(self):
        s = self.response_text_field.get_selected()
        self.wiki_pages_text_field.add_text(s+"\n")
        #self.wiki_pages_text_field.set_text(s)

    def clear_pageviews_callback(self):
        self.wiki_pages_text_field.clear()

    def search_wiki_callback(self):
        key_list = self.topic_text_field.get_list("\n")
        result_list = []
        for keyword in key_list:
            if len(keyword) > 2:
                page_list = ws.get_closet_wiki_page_list(keyword, n=7, cutoff=0.4)
                s = " | ".join(page_list)
                self.log_action("search term", {keyword: s.replace(",", " ")})
                result_list.extend(page_list)
        result = "\n".join(result_list)
        self.response_text_field.set_text(result)


    def test_pages_callback(self):
        granularity = self.sample_list.get_selected()
        start_dt = self.start_date_field.get_date()
        end_dt = self.end_date_field.get_date()
        topic_list = self.wiki_pages_text_field.get_list("\n")
        topic:str
        self.multi_count_list = []
        self.totals_dict = {}
        log_dict = {"granularity":granularity, "wiki_start": start_dt.strftime("%Y-%m-%d"), "wiki_end":end_dt.strftime("%Y-%m-%d")}
        for topic in topic_list:
            if len(topic) > 2:
                query = topic.replace(" ", "_")
                query = query.replace("&", "%26")
                view_list, totals = ws.get_pageview_list(query, start_dt, end_dt, granularity, self.user_agent)
                print("{} = {}".format(query, totals))
                self.totals_dict[topic] = totals
                view_list = sorted(view_list, key=lambda x: x.timestamp)
                self.multi_count_list.append(view_list)

        for k, v in self.totals_dict.items():
            log_dict[k.replace(",", " ")] = v
        self.log_action("test_keyword", log_dict)

        self.plot_callback()

    def plot_callback(self):
        if len(self.multi_count_list) == 0:
            message.showwarning("Plot Error", "You need something to plot first!")
            return

        #plt.title("\n".join("{}: {:,}".format(k, v) for k, v in self.totals_dict.items()), loc='left')
        for count_list in self.multi_count_list:
            y_vals = []
            dates = []
            vd:ws.ViewData
            for vd in count_list:
                y_vals.append(vd.views)
                dates.append(vd.timestamp)
            plt.plot(dates, y_vals)
        plt.yscale("log")
        #plt.gca().legend(self.totals_dict.keys())
        plt.gca().legend(["{}: {:,}".format(k, v) for k, v in self.totals_dict.items()])
        plt.gcf().autofmt_xdate()
        plt.show()

    def save_callback(self):
        initial_file = self.experiment_field.get_text()+".xlsx"
        filename = filedialog.asksaveasfilename(filetypes=(("Excel files", "*.xlsx"),("All Files", "*.*")), title="Save Excel File", initialfile=initial_file)
        if filename:
            print("saving to {}".format(filename))
            l = []

            for i in range(len(self.multi_count_list)):
                count_list = self.multi_count_list[i]
                vd:ws.ViewData
                vd = count_list[0]
                d = {"page":vd.article}
                l.append(d)
                for vd in count_list:
                    start_time_str = vd.timestamp.strftime('%Y-%m-%d')
                    d[start_time_str] = vd.views
            df = pd.DataFrame(l)
            with pd.ExcelWriter(filename) as writer:
                df.to_excel(writer, sheet_name='Page Views')
                writer.save()
            self.log_action("save", {"filename":filename})

    def save_page_text_callback(self):
        folder_selected = filedialog.askdirectory()
        topic_list = self.wiki_pages_text_field.get_list("\n")
        for topic in topic_list:
            if len(topic) > 2:
                print("Getting text for page [{}]:".format(topic))
                s = ws.get_page(topic, debug=False)
                filename = "{}/{}.txt".format(folder_selected, topic)
                print("\tSaving to {}".format(filename))
                with open(filename, 'w', encoding="utf-8") as f:
                    f.write(s)
                # print("{}\n\t{}".format(filename, s))

    def show_pages_callback(self):
        topic_list = self.wiki_pages_text_field.get_list("\n")
        for topic in topic_list:
            query = topic.replace(" ", "_")
            query = query.replace("&", "%26")
            url_str = "https://en.wikipedia.org/wiki/{}".format(query)
            webbrowser.open(url_str)

    def set_time_sample_callback(self, event:tk.Event = None):
        sample_str = self.sample_list.get_selected()
        self.sample_list.set_label("Sample\n({})".format(sample_str))

    def get_description_df(self, probe:str, response:str) -> pd.DataFrame:
        now = datetime.now()
        now_str = now.strftime("%B_%d_%Y_(%H:%M:%S)")
        sample_str = self.sample_list.get_selected()

        description_dict = {'name':getpass.getuser(), 'date':now_str, 'probe':probe, 'response':response, 'sampling':sample_str}
        df = pd.DataFrame.from_dict(description_dict, orient='index', columns=['Value'])
        return df

def main():
    app = WikiPageviewExplorer()
    app.mainloop()

if __name__ == "__main__":
    main()