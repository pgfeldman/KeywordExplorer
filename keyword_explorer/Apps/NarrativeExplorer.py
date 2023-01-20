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
    generate_tokens: DataField
    experiment_combo: TopicComboExt
    new_experiment_button:Buttons
    pca_dim_param: LabeledParam
    eps_param: LabeledParam
    min_samples_param: LabeledParam
    perplexity_param: LabeledParam

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("NarrativeExplorer")

    def setup_app(self):
        self.app_name = "NarrativeExplorer"
        self.app_version = "1.17.2023"
        self.geom = (600, 620)
        self.oai = OpenAIComms()
        self.msi = MySqlInterface(user_name="root", db_name="narrative_maps")
        self.mr = ManifoldReduction()

        if not self.oai.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'OPENAI_KEY'")

        self.experiment_id = -1

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
        buttons.add_button("Create New", self.implement_me)
        buttons.add_button("Update", self.implement_me)
        row = buttons.get_next_row()

        s = ttk.Style()
        s.configure('TNotebook.Tab', font=self.default_font)

        # Add the tabs
        tab_control = ttk.Notebook(self)
        tab_control.grid(column=0, row=row, columnspan=2, sticky="nsew")
        gpt_tab = ttk.Frame(tab_control)
        tab_control.add(gpt_tab, text='Generate')
        self.build_generator_tab(gpt_tab)

        embed_tab = ttk.Frame(tab_control)
        tab_control.add(embed_tab, text='Embedding')
        self.build_embed_tab(embed_tab)

        row += 1
        return row

    def build_generator_tab(self, tab: ttk.Frame):
        engine_list = self.oai.list_models(keep_list = ["davinci"], exclude_list = ["embed", "similarity", "code", "edit", "search", "audio", "instruct", "2020", "if", "insert"])
        row = 0
        self.generate_model_combo = TopicComboExt(tab, row, "Model:", self.dp, entry_width=25, combo_width=25)
        self.generate_model_combo.set_combo_list(sorted(engine_list))
        self.generate_model_combo.set_text(engine_list[0])
        self.generate_model_combo.tk_combo.current(0)
        row = self.generate_model_combo.get_next_row()
        self.generate_tokens = DataField(tab, row, "Tokens")
        self.generate_tokens.set_text("256")
        row = self.generate_tokens.get_next_row()

    def build_embed_tab(self, tab: ttk.Frame):
        engine_list = self.oai.list_models(keep_list = ["embedding"])
        row = 0
        self.embed_model_combo = TopicComboExt(tab, row, "Engine:", self.dp, entry_width=25, combo_width=25)
        self.embed_model_combo.set_combo_list(engine_list)
        self.embed_model_combo.set_text(engine_list[0])
        self.embed_model_combo.tk_combo.current(0)
        row = self.embed_model_combo.get_next_row()

def main():
    app = NarrativeExplorer()
    app.mainloop()

if __name__ == "__main__":
    main()