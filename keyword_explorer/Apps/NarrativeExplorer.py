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

class NarrativeExplorer(AppBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("NarrativeExplorer")

    def setup_app(self):
        self.app_name = "NarrativeExplorer"
        self.app_version = "1.17.2023"
        self.geom = (600, 150)

def main():
    app = NarrativeExplorer()
    app.mainloop()

if __name__ == "__main__":
    main()