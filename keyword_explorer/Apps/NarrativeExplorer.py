'''
Load - Loads an existing experiment
Model Selection - Various models of the GPT-3 or a local model
Prompt - "Once upon a time there was." or potentially much longer, paragraph-sized so lots of room. Also UTF-8 to handle other languages
Parameters - number of tokens, etc.
Run - sends the prompt to the GPT and gets the text response. A checkbox indicates if there should be automatic embedding
Clear embeddings
Get Embeddings
Extend - uses the existing prompt and response as a prompt
Cluster - happens on line boundaries. There should be an editable regex for that. Same sort of PCA/T-SNE as embedding explorer, which means there needs to be parameter tweaking. Clustering will have to be re-run multiple times, though I hope the embedding step is run once. To avoid the complexity of the interactive plotting, I think I'll just label the clusters (https://stackoverflow.com/questions/44998205/labeling-points-in-matplotlib-scatterplot)
Query - 1) Run cluster queries on the DB. Select the cluster ID and the number of responses. 2) Get the number of responses per cluster
Save - stores the text on a sentence-by sentence bases with clustering info
Generate Graph - runs through each narrative in an experiment to produce a directed graph of nodes. The output is all the narratives threaded together. Used as an input to Gephi
'''

import re
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as message
from datetime import datetime
from tkinter import filedialog
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors

import pandas as pd

from keyword_explorer.Apps.AppBase import AppBase
from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.ToolTip import ToolTip
from keyword_explorer.tkUtils.DateEntryField import DateEntryField
from keyword_explorer.tkUtils.ListField import ListField
from keyword_explorer.tkUtils.TextField import TextField
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.TopicComboExt import TopicComboExt

from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms
from keyword_explorer.utils.MySqlInterface import MySqlInterface
from keyword_explorer.utils.ManifoldReduction import ManifoldReduction, EmbeddedText
from keyword_explorer.tkUtils.LabeledParam import LabeledParam

from typing import List

class NarrativeExplorer(AppBase):
    oai: OpenAIComms
    msi: MySqlInterface
    mr: ManifoldReduction
    embed_model_combo: TopicComboExt
    generate_model_combo: TopicComboExt
    tokens_param: LabeledParam
    temp_param: LabeledParam
    presence_param: LabeledParam
    frequency_param: LabeledParam
    experiment_combo: TopicComboExt
    new_experiment_button:Buttons
    pca_dim_param: LabeledParam
    eps_param: LabeledParam
    min_samples_param: LabeledParam
    perplexity_param: LabeledParam
    prompt_text_field:TextField
    response_text_field:TextField
    embed_state_text_field:TextField
    regex_field:DataField
    saved_prompt_text:str
    saved_response_text:str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("NarrativeExplorer")
        self.text_width = 60
        self.label_width = 15

    def setup_app(self):
        self.app_name = "NarrativeExplorer"
        self.app_version = "1.20.2023"
        self.geom = (600, 620)
        self.oai = OpenAIComms()
        self.msi = MySqlInterface(user_name="root", db_name="narrative_maps")
        self.mr = ManifoldReduction()

        if not self.oai.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'OPENAI_KEY'")

        self.experiment_id = -1
        self.saved_prompt_text = "unset"
        self.saved_response_text = "unset"

    def experiment_callback(self, event:tk.Event):
        print("experiment_callback: event = {}".format(event))
        num_regex = re.compile(r"\d+")
        s = self.experiment_combo.tk_combo.get()
        self.experiment_combo.set_text(s)
        self.experiment_field.set_text(s)
        self.experiment_id = num_regex.findall(s)[0]
        print("experiment_callback: experiment_id = {}".format(self.experiment_id))

    def build_app_view(self, row: int, text_width: int, label_width: int) -> int:
        experiments = ["1 exp_1", "2 exp_2", "3 exp_3"]
        print("build_app_view")

        self.experiment_combo = TopicComboExt(self, row, "Saved Experiments:", self.dp, entry_width=20, combo_width=20)
        self.experiment_combo.set_combo_list(experiments)
        self.experiment_combo.set_callback(self.experiment_callback)
        row = self.experiment_combo.get_next_row()
        buttons = Buttons(self, row, "Experiments")
        buttons.add_button("Create", self.implement_me)
        buttons.add_button("Update", self.implement_me)
        row = buttons.get_next_row()

        s = ttk.Style()
        s.configure('TNotebook.Tab', font=self.default_font)

        # Add the tabs
        tab_control = ttk.Notebook(self)
        tab_control.grid(column=0, row=row, columnspan=2, sticky="nsew")
        gpt_tab = ttk.Frame(tab_control)
        tab_control.add(gpt_tab, text='Generate')
        self.build_generator_tab(gpt_tab, text_width, label_width)

        embed_tab = ttk.Frame(tab_control)
        tab_control.add(embed_tab, text='Embedding')
        self.build_embed_tab(embed_tab, text_width, label_width)

        row += 1
        return row

    def build_generator_tab(self, tab: ttk.Frame, text_width:int, label_width:int):
        engine_list = self.oai.list_models(keep_list = ["davinci"], exclude_list = ["embed", "similarity", "code", "edit", "search", "audio", "instruct", "2020", "if", "insert"])
        engine_list = sorted(engine_list)
        row = 0
        self.generate_model_combo = TopicComboExt(tab, row, "Model:", self.dp, entry_width=25, combo_width=25)
        self.generate_model_combo.set_combo_list(engine_list)
        self.generate_model_combo.set_text(engine_list[0])
        self.generate_model_combo.tk_combo.current(0)
        row = self.generate_model_combo.get_next_row()
        row = self.build_generate_params(tab, row)

        self.prompt_text_field = TextField(tab, row, "Prompt:", text_width, height=6, label_width=label_width)
        self.prompt_text_field.set_text("Once upon a time there was")
        ToolTip(self.prompt_text_field.tk_text, "The prompt that the GPT will use to generate text from")
        row = self.prompt_text_field.get_next_row()

        self.response_text_field = TextField(tab, row, 'Response:', text_width, height=11, label_width=label_width)
        ToolTip(self.response_text_field.tk_text, "The response from the GPT will be displayed here")
        row = self.response_text_field.get_next_row()

        self.regex_field = DataField(tab, row, 'Parse regex:', text_width, label_width=label_width)
        self.regex_field.set_text(r"\n|[\.!?] |([\.!?]\")")
        ToolTip(self.regex_field.tk_entry, "The regex used to parse the GPT response. Editable")
        row = self.regex_field.get_next_row()

        buttons = Buttons(tab, row, "Actions")
        buttons.add_button("Generate", self.new_prompt_callback)
        buttons.add_button("Add", self.extend_prompt_callback)
        buttons.add_button("Parse", self.parse_response_callback)
        buttons.add_button("Save", self.implement_me)
        buttons.add_button("Test Data", self.test_data_callback)

    def build_embed_tab(self, tab: ttk.Frame, text_width:int, label_width:int):
        engine_list = self.oai.list_models(keep_list = ["embedding"])
        row = 0
        self.embed_model_combo = TopicComboExt(tab, row, "Engine:", self.dp, entry_width=25, combo_width=25)
        self.embed_model_combo.set_combo_list(engine_list)
        self.embed_model_combo.set_text(engine_list[0])
        self.embed_model_combo.tk_combo.current(0)
        row = self.embed_model_combo.get_next_row()
        row = self.build_embed_params(tab, row)
        self.embed_state_text_field = TextField(tab, row, "Embed state:", text_width, height=10, label_width=label_width)
        ToolTip(self.embed_state_text_field.tk_text, "Embedding progess")
        row = self.embed_state_text_field.get_next_row()
        buttons = Buttons(tab, row, "Commands", label_width=10)
        b = buttons.add_button("GPT embed", self.implement_me, -1)
        b = buttons.add_button("Retreive", self.implement_me, -1)
        ToolTip(b, "Get the high-dimensional embeddings from the DB")
        b = buttons.add_button("Reduce", self.implement_me, -1)
        ToolTip(b, "Reduce to 2 dimensions with PCS and TSNE")
        b = buttons.add_button("Cluster", self.implement_me, -1)
        ToolTip(b, "Compute clusters on reduced data")
        b = buttons.add_button("Plot", self.implement_me, -1)
        ToolTip(b, "Plot the clustered points using PyPlot")
        b = buttons.add_button("Topics", self.implement_me, -1)
        ToolTip(b, "Use GPT to guess at topic names for clusters\n(not implemented)")
        row = buttons.get_next_row()

    def build_generate_params(self, parent:tk.Frame, row:int) -> int:
        f = tk.Frame(parent)
        f.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=1, pady=1)

        self.tokens_param = LabeledParam(f, 0, "Tokens:")
        self.tokens_param.set_text('256')
        ToolTip(self.tokens_param.tk_entry, "The number of the model will generate")

        self.temp_param = LabeledParam(f, 2, "Temp:")
        self.temp_param.set_text('0.7')
        ToolTip(self.temp_param.tk_entry, "The randomness of the response (0.0 - 1.0)")

        self.presence_param = LabeledParam(f, 4, "Presence penalty:")
        self.presence_param.set_text('0.3')
        ToolTip(self.presence_param.tk_entry, "Increases liklihood of new topics")


        self.frequency_param = LabeledParam(f, 6, "Frequency penalty:")
        self.frequency_param.set_text('0.3')
        ToolTip(self.frequency_param.tk_entry, "Supresses repeating text")
        return row + 1


    def build_embed_params(self, parent:tk.Frame, row:int) -> int:
        f = tk.Frame(parent)
        f.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=1, pady=1)
        self.pca_dim_param = LabeledParam(f, 0, "PCA Dim:")
        self.pca_dim_param.set_text('10')
        ToolTip(self.pca_dim_param.tk_entry, "The number of dimensions that the PCA\nwill reduce the original vectors to")
        self.eps_param = LabeledParam(f, 2, "EPS:")
        self.eps_param.set_text('8')
        ToolTip(self.eps_param.tk_entry, "DBSCAN: Specifies how close points should be to each other to be considered a part of a \ncluster. It means that if the distance between two points is lower or equal to \nthis value (eps), these points are considered neighbors.")
        self.min_samples_param = LabeledParam(f, 4, "Min Samples:")
        self.min_samples_param.set_text('5')
        ToolTip(self.min_samples_param.tk_entry, "DBSCAN: The minimum number of points to form a dense region. For \nexample, if we set the minPoints parameter as 5, then we need at least 5 points \nto form a dense region.")
        self.perplexity_param = LabeledParam(f, 6, "Perplex:")
        self.perplexity_param.set_text('80')
        ToolTip(self.perplexity_param.tk_entry, "T-SNE: The size of the neighborhood around each point that \nthe embedding attempts to preserve")
        return row + 1

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
        self.oai.max_tokens = self.tokens_param.get_as_int()
        self.oai.temperature = self.temp_param.get_as_float()
        self.oai.frequency_penalty = self.frequency_param.get_as_float()
        self.oai.presence_penalty = self.presence_param.get_as_float()
        self.oai.engine = self.generate_model_combo.get_text()

        results = self.oai.get_prompt_result(prompt, False)
        self.dp.dprint("\n------------\ntokens = {}, engine = {}\nprompt = {}".format(self.oai.max_tokens, self.oai.engine, prompt))
        self.log_action("gpt_prompt", {"tokens":self.oai.max_tokens, "engine":self.oai.engine, "prompt":prompt})

        # clean up before returning
        s = results[0].strip()
        self.log_action("gpt_response", {"gpt_text":s})
        return s

    def new_prompt_callback(self):
        prompt = self.prompt_text_field.get_text()
        response = self.get_gpt3_response(prompt)
        self.response_text_field.set_text(response)

    def extend_prompt_callback(self):
        prompt = "{} {}".format(self.prompt_text_field.get_text(), self.response_text_field.get_text())
        self.prompt_text_field.set_text(prompt)
        self.response_text_field.clear()

    def get_list(self, to_parse:str, regex_str:str = ",") -> List:
        rlist = re.split(regex_str, to_parse)
        to_return = []
        for t in rlist:
            if t != None:
                to_return.append(t.strip())
        to_return = [x for x in to_return if x] # filter out the blanks
        return to_return

    def parse_response_callback(self):
        # get the regex
        split_regex = self.regex_field.get_text()

        # get the prompt and respnse text blocks
        self.saved_prompt_text = self.prompt_text_field.get_text()
        self.saved_response_text = self.response_text_field.get_text()
        full_text = self.saved_prompt_text + self.saved_response_text

        # build the list of parsed text
        full_list = self.get_list(full_text, split_regex)
        # print(response_list)

        if len(full_list) > 1:
            self.response_text_field.clear()
            s = ""
            count = 0
            for r in full_list:
                if len(r) > 1:
                    s = "{}\n[{}] {}".format(s, count, r)
                    count += 1

            self.response_text_field.set_text(s)
        else:
            message.showwarning("Parse Error",
                                "Could not parse [{}]".format(self.response_text_field.get_text()))

    # make this a "restore" button?
    def test_data_callback(self):
        prompt_text = '''Once upon a time there was a man who had been a soldier, and who had fought in the wars. After some years he became tired of fighting, and he stopped his soldiering and went away to live by himself in the mountains. He built a hut for himself, and there he lived for many years. At last one day there was a knocking at his door. He opened it and found no one there.

The next day, and the next, and the next after that there was a knocking at his door, but when he opened it no one was ever there.

At last he got so cross that he could not keep away from home any more than usual. When he opened the door and found no one there, he was so angry that he threw a great stone after whoever it was that knocked.

Presently a voice called out to him and said: “I am coming back soon again; you must be careful not to throw stones at me then”; but the voice did not say who it was that spoke.

The second time the man’s heart failed him as soon as he opened his door; but when he heard the voice saying: “Be careful not to throw stones this time,” he felt quite sure that'''
        response_text = '''it was the same voice. Then he knew that it was his Guardian Spirit that spoke to him.

The third time the man was not afraid, but as soon as he opened the door and saw no one, he threw stones at it.

Then a great storm arose and the thunder rolled among the mountains, and the lightning flashed in his eyes and blinded him, and all about him there were voices shouting: “It is your Guardian Spirit that you have killed!”

And when he could see again, he looked up and saw that the hut had disappeared and that in its place stood a dark pine-tree. He ran to look for his hut, but it was nowhere to be found; he looked up and down the valley, but there was no sign of it anywhere. He called out loudly for his hut to come back,—but it never came back again. The hut had become a big pine-tree, and even the Guardian Spirit could not make it come back again.'''
        self.prompt_text_field.set_text(prompt_text)
        self.response_text_field.set_text(response_text)


def main():
    app = NarrativeExplorer()
    app.mainloop()

if __name__ == "__main__":
    main()