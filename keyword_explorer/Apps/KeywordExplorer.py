import getpass
import tkinter as tk
import tkinter.messagebox as message
from datetime import datetime, timedelta
from tkinter import filedialog

import pandas as pd

from keyword_explorer.Apps.AppBase import AppBase
from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms
from keyword_explorer.TwitterV2.TwitterV2Counts import TwitterV2Counts, TwitterV2Count
from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.DateEntryField import DateEntryField
from keyword_explorer.tkUtils.ListField import ListField
from keyword_explorer.tkUtils.TextField import TextField


class KeywordExplorer(AppBase):
    oai:OpenAIComms
    tvc:TwitterV2Counts
    prompt_text_field:TextField
    response_text_field:TextField
    keyword_text_field:TextField
    start_date_field:DateEntryField
    end_date_field:DateEntryField
    regex_field:DataField
    max_chars_field:DataField
    token_list:ListField
    engine_list:ListField
    sample_list:ListField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("KeywordExplorer")

    def setup_app(self):
        self.app_name = "KeywordExplorer"
        self.app_version = "4.5.22"
        self.geom = (850, 670)
        self.oai = OpenAIComms()
        self.tvc = TwitterV2Counts()

        if not self.oai.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'OPENAI_KEY'")
        if not self.tvc.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'BEARER_TOKEN_2'")


    def build_app_view(self, row:int, main_text_width:int, main_label_width:int) -> int:
        param_text_width = 15
        param_label_width = 15
        row += 1

        lf = tk.LabelFrame(self, text="GPT")
        lf.grid(row=row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_gpt(lf, main_text_width, main_label_width)

        lf = tk.LabelFrame(self, text="GPT Params")
        lf.grid(row=row, column=2, sticky="nsew", padx=5, pady=2)
        self.build_gpt_params(lf, param_text_width, param_label_width)
        row += 1

        lf = tk.LabelFrame(self, text="Twitter")
        lf.grid(row=row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_twitter(lf, main_text_width, main_label_width)

        lf = tk.LabelFrame(self, text="Twitter Params")
        lf.grid(row=row, column=2, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_twitter_params(lf, param_text_width, param_label_width)

        self.end_date_field.set_date()
        self.start_date_field.set_date(d = (datetime.utcnow() - timedelta(days=10)))

    def build_gpt(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.prompt_text_field = TextField(lf, row, "Prompt:\nDefault style:\nHere's a list of X:\n1)", text_width, height=5, label_width=label_width)
        self.prompt_text_field.set_text("Here's a short list of popular pets:\n1)")
        row = self.prompt_text_field.get_next_row()
        self.response_text_field = TextField(lf, row, 'Response', text_width, height=10, label_width=label_width)
        row = self.response_text_field.get_next_row()
        self.max_chars_field = DataField(lf, row, 'Max chars:', text_width, label_width=label_width)
        self.max_chars_field.set_text('20')
        row = self.max_chars_field.get_next_row()
        self.regex_field = DataField(lf, row, 'Parse regex', text_width, label_width=label_width)
        self.regex_field.set_text(r"\n[0-9]+\)|\n[0-9]+|[0-9]+\)")
        row = self.regex_field.get_next_row()
        buttons = Buttons(lf, row, "Actions", label_width=label_width)
        buttons.add_button("New prompt", self.new_prompt_callback)
        buttons.add_button("Extend prompt", self.extend_prompt_callback)
        buttons.add_button("Parse response", self.parse_response_callback)
        row = buttons.get_next_row()

    def build_gpt_params(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.token_list = ListField(lf, row, "Tokens", width=text_width, label_width=label_width, static_list=True)
        self.token_list.set_text(text='32, 64, 128, 256')
        self.token_list.set_callback(self.set_tokens_callback)
        row = self.token_list.get_next_row()

        self.engine_list = ListField(lf, row, "Engines", width=text_width, label_width=label_width, static_list=True)
        self.engine_list.set_text(list=self.oai.engines)
        self.engine_list.set_callback(self.set_engine_callback)
        row = self.engine_list.get_next_row()
        #
        # lbl = tk.Label(lf, text="Tokens", width=label_width, bg="red")
        # lbl.grid(row=row, column=0, sticky="w", padx=2, pady=2)

    def build_twitter(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.keyword_text_field = TextField(lf, row, 'Test Keyword(s)', text_width, height=1, label_width=label_width)
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

    def set_engine_callback(self, event:tk.Event = None):
        engine_str = self.engine_list.get_selected()
        self.engine_list.set_label("Engines\n({})".format(engine_str))

    def set_tokens_callback(self, event:tk.Event = None):
        token_str = self.token_list.get_selected()
        self.token_list.set_label("Tokens\n({})".format(token_str))

    def set_time_sample_callback(self, event:tk.Event = None):
        sample_str = self.sample_list.get_selected()
        self.sample_list.set_label("Sample\n({})".format(sample_str))

    def adjust_tokens(self) -> int:
        tokens = self.token_list.get_selected()
        tint = int(tokens)
        return tint

    def new_prompt_callback(self):
        prompt = self.prompt_text_field.get_text()
        response = self.get_gpt3_response(prompt)
        self.response_text_field.set_text(response)

    def extend_prompt_callback(self):
        prompt = "{}{}".format(self.prompt_text_field.get_text(), self.response_text_field.get_text())
        self.prompt_text_field.set_text(prompt)
        response = self.get_gpt3_response(prompt)
        self.response_text_field.set_text(response)

    def parse_response_callback(self):
        split_regex = self.regex_field.get_text()
        response_list = self.response_text_field.get_list(split_regex)
        print(response_list)

        if len(response_list) > 1:
            s:str = ""
            max_chars = self.max_chars_field.get_as_int()
            for r in response_list:
                if len(r) < max_chars:
                    s += r+"\n"
            #s = '\n'.join(response_list)
            self.keyword_text_field.set_text(s.strip())
        else:
            message.showwarning("Parse Error",
                                "Could not parse [{}]".format(self.response_text_field.get_text()))

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
        log_dict = {"granularity":granularity, "twitter_start": start_dt.strftime("%Y-%m-%d"), "twitter_end":end_dt.strftime("%Y-%m-%d")}
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

        for k, v in self.tvc.totals_dict.items():
            log_dict[k] = v
        self.log_action("test_keyword", log_dict)
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
                self.log_action("save", {"filename":filename})

    def launch_twitter_callback(self):
        key_list = self.keyword_text_field.get_list("\n")
        start_dt = self.start_date_field.get_date()
        end_dt = self.end_date_field.get_date()
        self.log_action("Launch_twitter", {"twitter_start": start_dt.strftime("%Y-%m-%d"), "twitter_end":end_dt.strftime("%Y-%m-%d"), "terms":" ".join(key_list)})
        self.tvc.launch_twitter(key_list, start_dt, end_dt)

    def get_description_df(self, probe:str, response:str) -> pd.DataFrame:
        now = datetime.now()
        now_str = now.strftime("%B_%d_%Y_(%H:%M:%S)")
        token_str = self.token_list.get_selected()
        engine_str = self.engine_list.get_selected()
        sample_str = self.sample_list.get_selected()

        description_dict = {'name':getpass.getuser(), 'date':now_str, 'probe':probe, 'response':response, 'sampling':sample_str, 'engine':engine_str, 'tokens':token_str}
        df = pd.DataFrame.from_dict(description_dict, orient='index', columns=['Value'])
        return df

    def get_gpt3_response(self, prompt:str) -> str:
        """
        Method that takes a prompt and gets the response back via the OpenAI API
        :param prompt: The prompt to be sent to the GPT-3
        :return: The GPT-3 Response
        """
        if len(prompt) < 3:
            self.dp.dprint("get_gpt3_response() Error. Prompt too short: '{}'".format(prompt))
            return ""

        # print(prompt)
        self.oai.max_tokens = self.adjust_tokens()
        self.oai.set_engine(name = self.engine_list.get_selected())
        results = self.oai.get_prompt_result(prompt, False)
        self.dp.dprint("\n------------\ntokens = {}, engine = {}\nprompt = {}".format(self.oai.max_tokens, self.oai.engine, prompt))
        self.log_action("gpt_prompt", {"tokens":self.oai.max_tokens, "engine":self.oai.engine, "prompt":prompt})

        # clean up before returning
        s = results[0].strip()
        s =  self.clean_list_text(s)
        self.log_action("gpt_response", {"gpt_text":s})
        return s

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
    app = KeywordExplorer()
    app.mainloop()

if __name__ == "__main__":
    main()