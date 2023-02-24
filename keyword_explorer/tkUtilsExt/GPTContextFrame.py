import re
import numpy as np
import tkinter as tk
from tkinter import ttk

from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.TextField import TextField
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.Checkboxes import Checkboxes, Checkbox
from keyword_explorer.tkUtils.TopicComboExt import TopicComboExt
from keyword_explorer.tkUtils.ToolTip import ToolTip
from keyword_explorer.tkUtils.GPT3GeneratorFrame import GPT3GeneratorFrame, GPT3GeneratorSettings

from typing import List, Dict, Callable

class GPTContextSettings(GPT3GeneratorSettings):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class GPTContextFrame(GPT3GeneratorFrame):
    keyword_filter:DataField
    context_prompt:DataField
    context_text_field:TextField
    prompt_query_cb:Checkbox

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def build_frame(self, frm: ttk.Frame, text_width:int, label_width:int):
        engine_list = self.oai.list_models(keep_list = ["davinci"], exclude_list = ["embed", "similarity", "code", "edit", "search", "audio", "instruct", "2020", "if", "insert"])
        engine_list = sorted(engine_list)
        row = 0
        self.generate_model_combo = TopicComboExt(frm, row, "Model:", self.dp, entry_width=25, combo_width=25)
        self.generate_model_combo.set_combo_list(engine_list)
        self.generate_model_combo.set_text(engine_list[0])
        self.generate_model_combo.tk_combo.current(0)
        ToolTip(self.generate_model_combo.tk_combo, "The GPT-3 model used to generate text")

        row = self.generate_model_combo.get_next_row()
        row = self.build_generate_params(frm, row)

        self.keyword_filter = DataField(frm, row, "Keywords:", text_width+20, label_width=label_width)
        self.keyword_filter.set_text("Pequod OR Rachel OR Ahab")
        ToolTip(self.keyword_filter.tk_entry, "Keywords to filter available data")
        row = self.keyword_filter.get_next_row()

        self.context_prompt = DataField(frm, row, "Context:", text_width+20, label_width=label_width)
        self.context_prompt.set_text("Working on whaling ships")
        ToolTip(self.context_prompt.tk_entry, "The prompt that will provide context")
        row = self.context_prompt.get_next_row()

        self.prompt_text_field = TextField(frm, row, "Prompt:", text_width, height=1, label_width=label_width)
        self.prompt_text_field.set_text("Why is Ahab obsessed with Moby Dick?")
        ToolTip(self.prompt_text_field.tk_text, "The prompt that the GPT will use to generate text from")
        row = self.prompt_text_field.get_next_row()

        cboxes = Checkboxes(frm, row, "Options")
        self.prompt_query_cb = cboxes.add_checkbox("Use Prompt for context", self.handle_checkboxes)
        self.prompt_query_cb.set_val(False)
        row = cboxes.get_next_row()

        # Add the tabs
        tab_control = ttk.Notebook(frm)
        tab_control.grid(column=0, row=row, columnspan=2, sticky="nsew")
        gen_tab = ttk.Frame(tab_control)
        tab_control.add(gen_tab, text='Generated')

        ctx_tab = ttk.Frame(tab_control)
        tab_control.add(ctx_tab, text='Context')

        self.response_text_field = TextField(gen_tab, row, 'Response:', text_width, height=11, label_width=label_width)
        ToolTip(self.response_text_field.tk_text, "The response from the GPT will be displayed here")

        self.context_text_field = TextField(ctx_tab, row, 'Context:', text_width, height=11, label_width=label_width)
        ToolTip(self.context_text_field.tk_text, "The context including the prompt")

        row = self.response_text_field.get_next_row()

        self.buttons = Buttons(frm, row, "Actions")
        b = self.buttons.add_button("Generate", self.new_prompt_callback)
        ToolTip(b, "Sends the prompt to the GPT")

    def handle_checkboxes(self, event = None):
        print("prompt_query_cb = {}".format(self.prompt_query_cb.get_val()))