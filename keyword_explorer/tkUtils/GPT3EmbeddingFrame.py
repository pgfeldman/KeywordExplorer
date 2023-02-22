import re
import numpy as np
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as message
from datetime import datetime
from tkinter import filedialog

from keyword_explorer.tkUtils.ConsoleDprint import ConsoleDprint
from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.ToolTip import ToolTip
from keyword_explorer.tkUtils.TextField import TextField
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.TopicComboExt import TopicComboExt

from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms
from keyword_explorer.tkUtils.LabeledParam import LabeledParam

from typing import List, Dict, Callable

class GPT3EmbeddingSettings:
    pca_dim:int
    eps:float
    min_samples:int
    perplexity:float

    def __init__(self, pca_dim = 5, eps = 64.0, min_samples = 4, perplexity = 2):
        self.pca_dim = pca_dim
        self.eps = eps
        self.min_samples = min_samples
        self.perplexity = perplexity

    def from_dict(self, d:Dict):
        if 'PCA_dimensions' in d:
            self.pca_dim = d['PCA_dimensions']
        if 'EPS' in d:
            self.eps = d['EPS']
        if 'min_samples' in d:
            self.min_samples = d['min_samples']
        if 'perplexity' in d:
            self.perplexity = d['perplexity']


class GPT3EmbeddingFrame:
    oai: OpenAIComms
    dp:ConsoleDprint
    generate_model_combo: TopicComboExt
    prompt_text_field:TextField
    response_text_field:TextField
    tokens_param: LabeledParam
    temp_param: LabeledParam
    presence_param: LabeledParam
    frequency_param: LabeledParam
    regex_field:DataField
    auto_field:DataField
    buttons:Buttons
    saved_prompt_text:str
    saved_response_text:str

    def __init__(self, oai:OpenAIComms, dp:ConsoleDprint):
        self.oai = oai
        self.dp = dp

    def build_frame(self, frm: ttk.Frame, text_width:int, label_width:int):
        engine_list = self.oai.list_models(keep_list = ["embedding"])
        row = 0
        self.embed_model_combo = TopicComboExt(frm, row, "Engine:", self.dp, entry_width=25, combo_width=25)
        self.embed_model_combo.set_combo_list(engine_list)
        self.embed_model_combo.set_text(engine_list[0])
        self.embed_model_combo.tk_combo.current(0)
        row = self.embed_model_combo.get_next_row()
        row = self.build_embed_params(frm, row)
        self.embed_state_text_field = TextField(frm, row, "Embed state:", text_width, height=10, label_width=label_width)
        ToolTip(self.embed_state_text_field.tk_text, "Embedding progess")
        row = self.embed_state_text_field.get_next_row()
        buttons = Buttons(frm, row, "Commands", label_width=10)
        b = buttons.add_button("GPT embed", self.get_oai_embeddings_callback, -1)
        ToolTip(b, "Get source embeddings from the GPT")
        b = buttons.add_button("Retreive", self.get_db_embeddings_callback, -1)
        ToolTip(b, "Get the high-dimensional embeddings from the DB")
        b = buttons.add_button("Reduce", self.reduce_dimensions_callback, -1)
        ToolTip(b, "Reduce to 2 dimensions with PCS and TSNE")
        b = buttons.add_button("Cluster", self.cluster_callback, -1)
        ToolTip(b, "Compute clusters on reduced data")
        b = buttons.add_button("Plot", self.plot_callback, -1)
        ToolTip(b, "Plot the clustered points using PyPlot")
        b = buttons.add_button("Topics", self.topic_callback, -1)
        ToolTip(b, "Use GPT to guess at topic names for clusters")
        row = buttons.get_next_row()

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