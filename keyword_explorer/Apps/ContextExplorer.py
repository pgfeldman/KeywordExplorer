import re
import getpass
import numpy as np
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
from keyword_explorer.tkUtils.Checkboxes import Checkboxes
from keyword_explorer.tkUtilsExt.GPTContextFrame import GPTContextFrame, GPTContextSettings
from keyword_explorer.tkUtils.ListField import ListField
from keyword_explorer.tkUtils.TextField import TextField
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.TopicComboExt import TopicComboExt
from keyword_explorer.tkUtils.LabeledParam import LabeledParam
from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms
from keyword_explorer.OpenAI.OpenAIEmbeddings import OpenAIEmbeddings
from keyword_explorer.utils.MySqlInterface import MySqlInterface
from keyword_explorer.utils.ManifoldReduction import ManifoldReduction, EmbeddedText, ClusterInfo
from keyword_explorer.utils.SharedObjects import SharedObjects

from typing import List, Dict

class ContextExplorer(AppBase):
    oai: OpenAIComms
    oae: OpenAIEmbeddings
    msi: MySqlInterface
    mr: ManifoldReduction
    so:SharedObjects
    gpt_frame: GPTContextFrame
    experiment_combo:TopicComboExt
    level_combo:TopicComboExt
    rows_field = DataField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("ContextExplorer")
        self.text_width = 60
        self.label_width = 15

        dt = datetime.now()
        experiment_str = "{}_{}_{}".format(self.app_name, getpass.getuser(), dt.strftime("%H:%M:%S"))
        self.experiment_field.set_text(experiment_str)
        self.load_experiment_list()
        # self.test_data_callback()

    def setup_app(self):
        self.app_name = "ContextExplorer"
        self.app_version = "2.23.2023"
        self.geom = (840, 670)
        self.oai = OpenAIComms()
        self.so = SharedObjects()
        self.msi = MySqlInterface(user_name="root", db_name="gpt_summary")
        self.gpt_frame = GPTContextFrame(self.oai, self.dp, self.so)

        if not self.oai.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'OPENAI_KEY'")

        self.saved_prompt_text = "unset"
        self.saved_response_text = "unset"
        self.experiment_id = -1
        self.run_id = -1
        self.parsed_full_text_list = []

    def build_app_view(self, row: int, text_width: int, label_width: int) -> int:
        print("build_app_view")
        self.generator_frame = GPTContextFrame(self.oai, self.dp, self.so)
        lf = tk.LabelFrame(self, text="GPT")
        lf.grid(row=row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_gpt(lf, text_width, label_width)

        lf = tk.LabelFrame(self, text="Params")
        lf.grid(row=row, column=2, sticky="nsew", padx=5, pady=2)
        self.build_params(lf, int(text_width/3), int(label_width/2))
        return row + 1

    def load_experiment_list(self):
        experiments = []
        results = self.msi.read_data("select * from table_source")
        for r in results:
            experiments.append("{}:{}".format(r['text_name'], r['group_name']))
        self.experiment_combo.set_combo_list(experiments)

    def get_levels_list(self):
        level_list = ['all', 'raw only', 'all summaries']
        if self.experiment_id != -1:
            sql = "select distinct level from table_summary_text where source = %s"
            vals = self.experiment_id
            results = self.msi.read_data(sql, vals)
            d:Dict
            for d in results:
                level_list.append(d['level'])
        self.level_combo.set_combo_list(level_list)
        self.level_combo.tk_combo.current(0)
        self.level_combo.clear()
        self.level_combo.set_text(self.level_combo.get_list()[0])

    def build_gpt(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.experiment_combo = TopicComboExt(lf, row, "Saved Projects:", self.dp, entry_width=20, combo_width=20)
        self.experiment_combo.set_callback(self.load_experiment_callback)
        row = self.experiment_combo.get_next_row()
        self.level_combo = TopicComboExt(lf, row, "Summary Levels:", self.dp, entry_width=20, combo_width=20)
        self.level_combo.set_callback(self.count_levels_callback)
        row = self.level_combo.get_next_row()
        buttons = Buttons(lf, row, "Experiments")
        b = buttons.add_button("Load", self.implement_me)
        ToolTip(b, "Load a project")
        row = buttons.get_next_row()

        s = ttk.Style()
        s.configure('TNotebook.Tab', font=self.default_font)

        # Add the tabs
        tab_control = ttk.Notebook(lf)
        tab_control.grid(column=0, row=row, columnspan=2, sticky="nsew")
        gpt_tab = ttk.Frame(tab_control)
        tab_control.add(gpt_tab, text='Generate')
        self.build_generator_tab(gpt_tab, text_width, label_width)

        corpora_tab = ttk.Frame(tab_control)
        tab_control.add(corpora_tab, text='Corpora')
        self.build_corpora_tab(corpora_tab, text_width, label_width)

        row += 1
        return row

    def build_params(self, lf:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.rows_field = DataField(lf, row, 'Rows:', text_width, label_width=label_width)
        row = self.rows_field.get_next_row()
        self

    def build_generator_tab(self, tab: ttk.Frame, text_width:int, label_width:int):
        self.generator_frame.build_frame(tab, text_width, label_width)

    def build_corpora_tab(self, tab: ttk.Frame, text_width:int, label_width:int):
        row = 0

        self.regex_field = DataField(tab, row, 'Parse regex:', text_width, label_width=label_width)
        self.regex_field.set_text(r"\n+|[\.!?()“”]+")
        ToolTip(self.regex_field.tk_entry, "The regex used to parse the file. Editable")
        row = self.regex_field.get_next_row()

        buttons = Buttons(tab, row, "Actions")
        b = buttons.add_button("Load File", self.implement_me())
        ToolTip(b, "Loads new text into a project, splits into chunks and finds embeddings")

    def load_experiment_callback(self, event = None):
        print("load_experiment_callback")
        s = self.experiment_combo.tk_combo.get()
        l = s.split(":")
        self.experiment_combo.clear()
        self.experiment_combo.set_text(s)
        results = self.msi.read_data("select id from table_source where text_name = %s and group_name = %s", (l[0],l[1]))
        if len(results) > 0:
            self.experiment_id = results[0]['id']
            self.experiment_field.set_text(" experiment {}: {}".format(self.experiment_id, s))

        self.get_levels_list()
        self.count_levels_callback()
        print("experiment_callback: experiment_id = {}".format(self.experiment_id))

    def count_levels_callback(self, event = None):
        if self.experiment_id == -1:
            tk.messagebox.showwarning("Warning!", "Please create or select a database first")
            return

        level = self.level_combo.tk_combo.get()
        self.level_combo.clear()
        self.level_combo.set_text(level)
        print("\nlevel = '{}'".format(level))

        raw_count = 0
        summary_count = 0
        if level == 'raw only' or level == 'all':
            print("'raw only' or 'all'")
            sql = "select count(*) from gpt_summary.table_parsed_text where source = %s"
            vals = (self.experiment_id,)
            results = self.msi.read_data(sql, vals)
            raw_count = int(results[0]['count(*)'])
            self.rows_field.set_text("{:,}".format(raw_count))
        if level == 'all summaries' or level == 'all':
            print("'all summaries' or 'all'")
            sql = "select count(*) from gpt_summary.table_summary_text where source = %s"
            vals = (self.experiment_id,)
            results = self.msi.read_data(sql, vals)
            summary_count = int(results[0]['count(*)'])
            self.rows_field.set_text("{:,}".format(summary_count))
        if level == 'all':
            print("'all'")
            self.rows_field.set_text("{:,}".format(raw_count + summary_count))

        try:
            level = int(level)
            print("level {}".format(level))
            sql = "select count(*) from gpt_summary.table_summary_text where level = %s and source = %s"
            vals = (level, self.experiment_id,)
            results = self.msi.read_data(sql, vals)
            count = int(results[0]['count(*)'])
            self.rows_field.set_text("{:,}".format(count))
        except ValueError:
            pass

def main():
    app = ContextExplorer()
    app.mainloop()

if __name__ == "__main__":
    main()