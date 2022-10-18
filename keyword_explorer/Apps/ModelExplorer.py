import re
import tkinter.messagebox as message
import tkinter.filedialog as filedialog
import tkinter as tk
from tkinter import ttk
from transformers import TFGPT2LMHeadModel, GPT2Tokenizer
import tensorflow as tf

from keyword_explorer.Apps.AppBase import AppBase
from keyword_explorer.tkUtils.TopicComboExt import TopicComboExt
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.LabeledParam import LabeledParam
from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.ToolTip import ToolTip
from keyword_explorer.tkUtils.MoveableNode import MovableNode
from keyword_explorer.tkUtils.Checkboxes import Checkboxes, DIR
from keyword_explorer.utils.MySqlInterface import MySqlInterface

from typing import Union, Dict, List, Pattern

class ModelExplorer(AppBase):
    msi: MySqlInterface
    tf_seed:int
    tokenizer:Union[None, GPT2Tokenizer]
    model:Union[None, TFGPT2LMHeadModel]
    sequence_regex:Pattern
    element_regex:Pattern

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("ModelExplorer")

    def setup_app(self):
        self.app_name = "ModelExplorer"
        self.app_version = "10.18.22"
        self.geom = (600, 620)
        self.msi = MySqlInterface(user_name="root", db_name="gpt_experiments")
        self.tokenizer = None
        self.model = None
        self.tf_seed = 2
        self.sequence_regex = re.compile(r"\]\]\[\[")
        self.element_regex = re.compile(r" \w+: ")

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

    def run_probes(self, probe_list:List, num_return_sequences:int = 10) -> Dict:
        if self.model == None or self.tokenizer == None:
            message.showwarning("GPT Model", "Model directory unset")
            return
        result_dict = {}
        for probe in probe_list:
            tf.random.set_seed(self.tf_seed)
            strings_list = []
            # encode context the generation is conditioned on
            input_ids = self.tokenizer.encode(probe, return_tensors='tf')

            # generate text until the output length (which includes the context length) reaches 50
            output_list  = self.model.generate(
                input_ids,
                do_sample=True,
                max_length=256,
                top_k=50,
                top_p=0.95,
                num_return_sequences=num_return_sequences)

            print("\n{}:".format(probe))
            parse_list = []
            for i, beam_output  in enumerate(output_list):
                output = self.tokenizer.decode(beam_output , skip_special_tokens=True)
                s = " ".join(output.split())
                # s = s.split(']]] [[[')[0]
                # print("\t[{}]: {}".format(i, s))
                parse_list.append(s)
                strings_list.append(s)

            result_dict[probe] = strings_list
        return result_dict

    def load_model_callback(self):
        path = filedialog.askdirectory(title="Load experiment")
        if path:
            self.dp.dprint("ModelExplorer.load_model_callback() loading {}".format(path))
            self.tokenizer = GPT2Tokenizer.from_pretrained(path)
            self.model = TFGPT2LMHeadModel.from_pretrained(path, pad_token_id=self.tokenizer.eos_token_id, from_pt=True)
            result_dict = self.run_probes(["[[text:"])
            p:str
            l:list
            for p, l in result_dict.items():
                print("{}:".format(p))
                for s in l:
                    print("\t{}".format(s))


    def setup(self):
        self.dp.dprint("pre-running setup")

def main():
    app = ModelExplorer()
    app.setup()
    app.mainloop()

if __name__ == "__main__":
    main()