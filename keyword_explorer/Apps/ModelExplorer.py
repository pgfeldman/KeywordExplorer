import re
import tkinter.messagebox as message
import tkinter.filedialog as filedialog
import tkinter as tk
from tkinter import ttk

from keyword_explorer.Apps.AppBase import AppBase
from keyword_explorer.tkUtils.TopicComboExt import TopicComboExt
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.LabeledParam import LabeledParam
from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.ToolTip import ToolTip
from keyword_explorer.tkUtils.Checkboxes import Checkboxes, DIR
from keyword_explorer.utils.MySqlInterface import MySqlInterface
from keyword_explorer.huggingface.HFaceGPT import HFaceGPT

from typing import Union, Dict, List, Pattern
class ModelExplorer(AppBase):
    probe_field:DataField
    max_length_param:LabeledParam
    top_k_param:LabeledParam
    top_p_param:LabeledParam
    num_seq_param:LabeledParam
    gpt_response_frame:tk.Text
    total_percent:LabeledParam
    ten_percent:LabeledParam
    twenty_percent:LabeledParam
    thirty_percent:LabeledParam
    forty_percent:LabeledParam
    msi: MySqlInterface
    sequence_regex:Pattern
    element_regex:Pattern
    hgpt:HFaceGPT

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("ModelExplorer")

    def setup_app(self):
        self.app_name = "ModelExplorer"
        self.app_version = "10.18.22"
        self.geom = (850, 750)
        self.msi = MySqlInterface(user_name="root", db_name="gpt_experiments")
        self.tokenizer = None
        self.model = None
        self.sequence_regex = re.compile(r"\]\]\[\[")
        self.element_regex = re.compile(r" \w+: ")
        self.hgpt = None

    def build_menus(self):
        print("building menus")
        self.option_add('*tearOff', tk.FALSE)
        menubar = tk.Menu(self)
        self['menu'] = menubar
        menu_file = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='Load model', command=self.load_model_callback)
        menu_file.add_command(label='Load IDs', command=self.load_ids_callback)
        menu_file.add_command(label='Exit', command=self.terminate)

    def build_app_view(self, row:int, text_width:int, label_width:int) -> int:
        row += 1
        lf = tk.LabelFrame(self, text="GPT-2")
        lf.grid(row=row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)

        self.text_width = 75
        self.build_probe(lf, self.text_width+20, label_width)

    def build_probe(self, parent:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        row = self.build_param_row(parent, row)
        row = self.build_percent_row(parent, row)

        self.probe_field = DataField(parent, row, "Probe:", text_width, label_width=label_width)
        ToolTip(self.probe_field.tk_entry, "Type your search term or phrase here")
        self.probe_field.set_text(']][[text: ')
        row = self.probe_field.get_next_row()

        buttons = Buttons(parent, row, "Actions:", label_width)
        buttons.add_button("Run", self.run_probe_callback)
        row = buttons.get_next_row()

        self.gpt_response_frame = tk.Text(parent)
        self.gpt_response_frame.grid(row = row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
        text_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.gpt_response_frame.yview)
        self.gpt_response_frame['yscrollcommand'] = text_scrollbar.set
        text_scrollbar.grid(column=2, row=row, rowspan=1, sticky=(tk.N, tk.S))
        ToolTip(self.gpt_response_frame, "Parsed responses from GPT are here")

    def build_param_row(self, parent:tk.Frame, row:int) -> int:
        f = tk.Frame(parent)
        f.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=1, pady=1)
        self.max_length_param = LabeledParam(f, 0, "Max Length:")
        self.max_length_param.set_text('128')
        ToolTip(self.max_length_param.tk_entry, "The length of each response")

        self.top_k_param = LabeledParam(f, 2, "Top K:")
        self.top_k_param.set_text('50')
        ToolTip(self.top_k_param.tk_entry, "The number of top tokens to sample from")

        self.top_p_param = LabeledParam(f, 4, "Min Samples:")
        self.top_p_param.set_text('0.95')
        ToolTip(self.top_p_param.tk_entry, "The number of top tokens to sample from")

        self.num_seq_param = LabeledParam(f, 6, "Num Sequences:")
        self.num_seq_param.set_text('10')
        ToolTip(self.num_seq_param.tk_entry, "The number of sequences generated in one shot by the GPT")

        return row + 1

    def build_percent_row(self, parent:tk.Frame, row:int) -> int:
        f = tk.Frame(parent)
        f.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=1, pady=1)
        self.total_percent = LabeledParam(f, 0, "Total:")
        self.total_percent.set_text('0')
        ToolTip(self.total_percent.tk_entry, "Number of generated texts")

        self.ten_percent = LabeledParam(f, 2, "Ten:")
        self.ten_percent.set_text('0')
        ToolTip(self.ten_percent.tk_entry, "'ten' percentage")

        self.twenty_percent = LabeledParam(f, 4, "Twenty:")
        self.twenty_percent.set_text('0')
        ToolTip(self.twenty_percent.tk_entry, "'twenty' percentage")

        self.thirty_percent = LabeledParam(f, 6, "Thirty:")
        self.thirty_percent.set_text('0')
        ToolTip(self.thirty_percent.tk_entry, "'thirty' percentage")

        self.forty_percent = LabeledParam(f, 8, "Forty:")
        self.forty_percent.set_text('0')
        ToolTip(self.forty_percent.tk_entry, "'forty' percentage")

        return row+1

    def run_probe_callback(self):
        probe = self.probe_field.get_text()
        s = "probe: '{}'".format(probe)
        self.gpt_response_frame.delete('1.0', tk.END)
        self.gpt_response_frame.insert("1.0", s)
        if self.hgpt == None:
            message.showwarning("GPT-2", "Model isn't loaded. Please select\ndirectory in the file menu")
            return
        self.dp.dprint("running probe {}".format(probe))
        result_list = self.hgpt.run_probes(probe)
        for result in result_list:
            sequence_list = self.hgpt.clean_and_split_sequence(result)
            count = 0
            for sequence in sequence_list:
                dict_list = self.hgpt.parse_sequence(sequence)
                d:Dict
                for d in dict_list: # get the text first
                    if d['word'] == 'text':
                        s += "sequence {} of {}\ntext: {}\n".format(count, len(sequence_list), d['substr'])
                        break
                for d in dict_list: #then the meta wrapping
                    if d['word'] != 'text':
                        s += "\t{}: {}\n".format(d['word'], d['substr'])
                s += "\n\n"
                count+= 1
        print(s)

        self.gpt_response_frame.delete('1.0', tk.END)
        self.gpt_response_frame.insert("1.0", s)


    def load_model_callback(self):
        path = filedialog.askdirectory(title="Load experiment")
        if path:
            self.dp.dprint("ModelExplorer.load_model_callback() loading {}".format(path))
            self.hgpt = HFaceGPT(path)
            self.dp.dprint("ModelExplorer.load_model_callback() loaded {}".format(path))

    def setup(self):
        self.dp.dprint("pre-running setup")

def main():
    app = ModelExplorer()
    app.setup()
    app.mainloop()

if __name__ == "__main__":
    main()