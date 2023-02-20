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