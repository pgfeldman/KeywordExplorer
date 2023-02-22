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
from keyword_explorer.tkUtils.GPT3GeneratorFrame import GPT3GeneratorSettings, GPT3GeneratorFrame
from keyword_explorer.tkUtils.ListField import ListField
from keyword_explorer.tkUtils.TextField import TextField
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.TopicComboExt import TopicComboExt

from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms
from keyword_explorer.OpenAI.OpenAIEmbeddings import OpenAIEmbeddings
from keyword_explorer.utils.MySqlInterface import MySqlInterface
from keyword_explorer.utils.ManifoldReduction import ManifoldReduction, EmbeddedText, ClusterInfo
from keyword_explorer.tkUtils.LabeledParam import LabeledParam

from typing import List, Dict

class ContextExplorer(AppBase):
    oai: OpenAIComms
    oae: OpenAIEmbeddings
    msi: MySqlInterface
    mr: ManifoldReduction
    gpt_frame: GPT3GeneratorFrame

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("NarrativeExplorer")
        self.text_width = 60
        self.label_width = 15

        dt = datetime.now()
        experiment_str = "{}_{}_{}".format(self.app_name, getpass.getuser(), dt.strftime("%H:%M:%S"))
        #self.experiment_field.set_text(experiment_str)
        #self.load_experiment_list()
        # self.test_data_callback()

    def setup_app(self):
        self.app_name = "ContextExplorer"
        self.app_version = "2.22.2023"
        self.geom = (840, 670)
        self.oai = OpenAIComms()
        self.msi = MySqlInterface(user_name="root", db_name="gpt_summary")
        self.gpt_frame = GPT3GeneratorFrame(self.oai, self.dp)

        if not self.oai.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'OPENAI_KEY'")

        self.saved_prompt_text = "unset"
        self.saved_response_text = "unset"
        self.experiment_id = -1
        self.run_id = -1
        self.parsed_full_text_list = []

def main():
    app = ContextExplorer()
    app.mainloop()

if __name__ == "__main__":
    main()