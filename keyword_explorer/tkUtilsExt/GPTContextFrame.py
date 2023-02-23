import re
import numpy as np
import tkinter as tk
from tkinter import ttk

from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.TextField import TextField
from keyword_explorer.tkUtils.Checkboxes import Checkboxes, Checkbox
from keyword_explorer.tkUtils.TopicComboExt import TopicComboExt
from keyword_explorer.tkUtils.ToolTip import ToolTip
from keyword_explorer.tkUtils.GPT3GeneratorFrame import GPT3GeneratorFrame, GPT3GeneratorSettings

from typing import List, Dict, Callable

class GPTContextSettings(GPT3GeneratorSettings):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class GPTContextFrame(GPT3GeneratorFrame):
    query_text_field:TextField
    keywords_cb:Checkbox
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

        self.query_text_field = TextField(frm, row, "Query:", text_width, height=2, label_width=label_width)
        self.query_text_field.set_text("Pequod OR Rachel OR Ahab")
        ToolTip(self.query_text_field.tk_text, "The search that will provide context")
        row = self.query_text_field.get_next_row()

        self.prompt_text_field = TextField(frm, row, "Prompt:", text_width, height=2, label_width=label_width)
        self.prompt_text_field.set_text("Why is Ahab obsessed with Moby Dick?")
        ToolTip(self.prompt_text_field.tk_text, "The prompt that the GPT will use to generate text from")
        row = self.prompt_text_field.get_next_row()

        cboxes = Checkboxes(frm, row, "Options")
        self.prompt_query_cb = cboxes.add_checkbox("Use Prompt for Query", self.handle_checkboxes)
        self.prompt_query_cb.set_val(False)
        self.keywords_cb = cboxes.add_checkbox("Match keywords", self.handle_checkboxes)
        self.keywords_cb.set_val(False)
        row = cboxes.get_next_row()

        self.response_text_field = TextField(frm, row, 'Response:', text_width, height=11, label_width=label_width)
        ToolTip(self.response_text_field.tk_text, "The response from the GPT will be displayed here")
        row = self.response_text_field.get_next_row()

        self.buttons = Buttons(frm, row, "Actions")
        b = self.buttons.add_button("Generate", self.new_prompt_callback)
        ToolTip(b, "Sends the prompt to the GPT")
        b = self.buttons.add_button("Add", self.extend_prompt_callback)
        ToolTip(b, "Adds the response to the prompt")
        b = self.buttons.add_button("Parse", self.parse_response_callback)
        ToolTip(b, "Parses the response into a list for embeddings")

    def handle_checkboxes(self, event = None):
        print("prompt_query_cb = {}".format(self.prompt_query_cb.get_val()))
        print("keywords_cb = {}".format(self.keywords_cb.get_val()))
