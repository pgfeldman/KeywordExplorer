import re
import json
from datetime import datetime
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
from keyword_explorer.tkUtils.Checkboxes import Checkboxes, Checkbox, DIR
from keyword_explorer.utils.MySqlInterface import MySqlInterface
from keyword_explorer.huggingface.HFaceGPT import HFaceGPT
from keyword_explorer.huggingface.PatternCounter import PatternCounters, PatternCounter

from typing import Union, Dict, List, Pattern
class ModelExplorer(AppBase):
    description_field:DataField
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
    flag_checkboxes:Checkboxes
    spreadsheet_checkbox:Checkbox
    seed_checkbox:Checkbox
    db_checkbox:Checkbox
    action_buttons:Buttons
    msi: MySqlInterface
    sequence_regex:Pattern
    element_regex:Pattern
    pattern_counters:PatternCounters
    hgpt:HFaceGPT
    reuse_seed:bool
    db_flag:bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("ModelExplorer")

    def setup_app(self):
        self.app_name = "ModelExplorer"
        self.app_version = "10.27.22"
        self.geom = (850, 750)
        self.msi = MySqlInterface(user_name="root", db_name="gpt_experiments")
        self.tokenizer = None
        self.model = None
        self.sequence_regex = re.compile(r"\]\]\[\[")
        self.element_regex = re.compile(r" \w+: ")
        self.hgpt = None
        self.pattern_counters = PatternCounters()
        self.pattern_counters.add(PatternCounter(r"\w+: ten"), "ten")
        self.pattern_counters.add(PatternCounter(r"\w+: twenty"), "twenty")
        self.pattern_counters.add(PatternCounter(r"\w+: thirty"), "thirty")
        self.pattern_counters.add(PatternCounter(r"\w+: forty"), "forty")
        self.reuse_seed = False
        self.db_flag = False

    def build_menus(self):
        print("building menus")
        self.option_add('*tearOff', tk.FALSE)
        menubar = tk.Menu(self)
        self['menu'] = menubar
        menu_file = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='Load experiment', command=self.load_experiment_callback)
        menu_file.add_command(label='Save experiment', command=self.save_experiment_callback)
        menu_file.add_command(label='Load model', command=self.load_model_callback)
        menu_file.add_command(label='Load IDs', command=self.load_ids_callback)
        menu_file.add_command(label='Exit', command=self.terminate)

    def build_app_view(self, row:int, text_width:int, label_width:int) -> int:
        row += 1
        self.description_field = DataField(self, row, "Description:", text_width, label_width=label_width)
        row = self.description_field.get_next_row()
        lf = tk.LabelFrame(self, text="GPT-2")
        lf.grid(row=row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)

        self.text_width = 75
        self.build_probe(lf, self.text_width+20, label_width)

    def build_probe(self, parent:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        row = self.build_param_row(parent, row)
        row = self.build_percent_row(parent, row)

        self.flag_checkboxes = Checkboxes(parent, row, "Flags")
        self.seed_checkbox = self.flag_checkboxes.add_checkbox("Re-use Seed", self.seed_callback, dir= DIR.COL )
        ToolTip(self.seed_checkbox.cb, "Use the same seed for each batch")
        self.db_checkbox = self.flag_checkboxes.add_checkbox("Save to DB", self.db_flag_callback, dir= DIR.COL )
        ToolTip(self.db_checkbox.cb, "Save the output to the gpt_experiments database")
        self.spreadsheet_checkbox = self.flag_checkboxes.add_checkbox("Save to spreadsheet", self.implement_me, dir= DIR.COL )
        ToolTip(self.spreadsheet_checkbox.cb, "Save the output to a spreadsheet\nNot implemented")
        row = self.flag_checkboxes.get_next_row()

        self.probe_field = DataField(parent, row, "Probe:", text_width, label_width=label_width)
        ToolTip(self.probe_field.tk_entry, "Type your comma-separated search\n terms or phrase here")
        self.probe_field.set_text(']][[text: ')
        row = self.probe_field.get_next_row()

        self.action_buttons = Buttons(parent, row, "Actions:", label_width)
        self.action_buttons.add_button("Run", self.run_probe_callback)
        row = self.action_buttons.get_next_row()

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

        self.top_p_param = LabeledParam(f, 4, "Top P:")
        self.top_p_param.set_text('0.95')
        ToolTip(self.top_p_param.tk_entry, "The percentage of top tokens to sample from")

        self.num_seq_param = LabeledParam(f, 6, "Num Sequences:")
        self.num_seq_param.set_text('10')
        ToolTip(self.num_seq_param.tk_entry, "The number of sequences generated in one shot by the GPT")

        self.batch_size_param = LabeledParam(f, 8, "Batch size:")
        self.batch_size_param.set_text('1')
        ToolTip(self.batch_size_param.tk_entry, "The number of sequence batches to run")

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

    def save_experiment_callback(self):
        d = {}
        d['probe_str'] = self.probe_field.get_text()
        d['description'] = self.description_field.get_text()
        d['max_len'] = self.max_length_param.get_as_int()
        d['top_k'] = self.top_k_param.get_as_int()
        d['top_p'] = self.top_p_param.get_as_float()
        d['num_sequences'] = self.num_seq_param.get_as_int()
        d['batch_size'] = self.batch_size_param.get_as_int()
        d['seed_flag'] = self.reuse_seed
        d['db_flag'] = self.db_flag
        if self.hgpt != None:
            d['model_path'] = self.hgpt.path_str
        self.save_experiment_json(d)

    def load_experiment_callback(self):
        result = filedialog.askopenfile(filetypes=(("JSON files", "*.json"),("All Files", "*.*")), title="Load experiment")
        if result:
            filename = result.name
            self.dp.dprint("AppBase.load_experiment_callback() loading {}".format(filename))
            with open(filename, encoding="utf8") as f:
                d:Dict = json.load(f)
                self.probe_field.set_text(self.safe_dict_read(d, 'probe_str', ']][[text:'))
                self.description_field.set_text(self.safe_dict_read(d, 'description', 'unset'))
                self.max_length_param.set_text(self.safe_dict_read(d, 'max_len', 128))
                self.top_k_param.set_text(self.safe_dict_read(d, 'top_k', 50))
                self.top_p_param.set_text(self.safe_dict_read(d, 'top_p', 0.95))
                self.num_seq_param.set_text(self.safe_dict_read(d, 'num_sequences', 128))
                self.batch_size_param.set_text(self.safe_dict_read(d, 'batch_size', 1))
                self.reuse_seed = self.safe_dict_read(d, 'seed_flag', False)
                self.seed_checkbox.set_val(self.reuse_seed)
                self.db_flag = self.safe_dict_read(d, 'db_flag', False)
                self.db_checkbox.set_val(self.db_flag)
                if "model_path" in d:
                    self.hgpt = HFaceGPT(d['model_path'])
                    self.calc_percents()

    def seed_callback(self):
        self.reuse_seed = not self.reuse_seed
        self.dp.dprint("reuse_seed = {}".format(self.reuse_seed))

    def db_flag_callback(self):
        self.db_flag = not self.db_flag
        self.dp.dprint("db_flag = {}".format(self.db_flag))

    def calc_percents(self):
        for s in self.hgpt.result_list:
            self.pattern_counters.evaluate(s)

        print("calc_percents() Total = {}".format(self.pattern_counters.get_total()))
        pc:PatternCounter
        for name, pc in self.pattern_counters.pc_dict.items():
            print("{} = {} {:.1f}%".format(name, pc.match_count, self.pattern_counters.get_percent(name)))

        self.ten_percent.set_text("{}%".format(int(self.pattern_counters.get_percent("ten"))))
        self.twenty_percent.set_text("{}%".format(int(self.pattern_counters.get_percent("twenty"))))
        self.thirty_percent.set_text("{}%".format(int(self.pattern_counters.get_percent("thirty"))))
        self.forty_percent.set_text("{}%".format(int(self.pattern_counters.get_percent("forty"))))
        self.total_percent.set_text(self.pattern_counters.get_total())

    def run_probe_callback(self):
        if self.hgpt == None:
            message.showwarning("GPT-2", "Model isn't loaded. Please select\ndirectory in the file menu")
            return
        max_len = self.max_length_param.get_as_int()
        top_k = self.top_k_param.get_as_int()
        top_p = self.top_p_param.get_as_float()
        num_sequences = self.num_seq_param.get_as_int()
        batch_size = self.batch_size_param.get_as_int()
        experiment_id = -1
        if self.db_flag:
            sql = "insert into gpt_experiments.table_experiment (description, model_name, date, probe_list, batch_size, do_sample, max_length, top_k, top_p, num_return_sequences) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            vals = (self.description_field.get_text(), self.hgpt.name, datetime.now(), self.probe_field.get_text(),
                    batch_size, True, max_len, top_k, top_p, num_sequences)
            experiment_id = self.msi.write_sql_values_get_row(sql, vals)
            self.dp.dprint("run_probe_callback() experiment_id = {}".format(experiment_id))

        probe_list = self.probe_field.get_text().split(",")
        for probe in probe_list:
            probe = probe.strip()
            self.dp.dprint("running probe {}".format(probe))
            seed_flag = self.reuse_seed
            s = "probe: '{}'".format(probe)
            for batch in range(batch_size):
                result_list = self.hgpt.run_probes(probe, num_return_sequences=num_sequences, top_k=top_k, top_p=top_p, max_length=max_len, reset_seed=seed_flag)
                seed_flag = False # We only want the seed reset once for each probe
                self.calc_percents()
                for result in result_list:
                    sequence_list = self.hgpt.clean_and_split_sequence(result)
                    count = 0
                    for sequence in sequence_list:
                        dict_list = self.hgpt.parse_sequence(sequence)
                        d:Dict
                        text_id = -1
                        for d in dict_list: # get the text first
                            if d['word'] == 'text':
                                s += "sequence {} of {}\ntext: {}\n".format(count, len(sequence_list), d['substr'])
                                if count == 1 and experiment_id != -1:
                                    sql = "insert into table_text (experiment_id, probe, text) VALUES (%s, %s, %s)"
                                    vals = (experiment_id, probe, d['substr'])
                                    text_id = self.msi.write_sql_values_get_row(sql, vals)
                                    self.dp.dprint("run_probe_callback() text_id = {}, probe = {}, text = {}".format(text_id, probe, d['substr']))
                                break
                        for d in dict_list: #then the meta wrapping
                            if d['word'] != 'text':
                                s += "\t{}: {}\n".format(d['word'], d['substr'])
                                if text_id != -1:
                                    sql = "insert into table_text_data (text_id, name, value) VALUES (%s, %s, %s)"
                                    vals = (text_id, d['word'], d['substr'])
                                    self.msi.write_sql_values_get_row(sql, vals)
                                    self.dp.dprint("run_probe_callback() name = {}, val = {}".format(text_id, d['word'], d['substr']))
                        s += "\n\n"
                        count+= 1
                print(s)
                s = self.clean_text(s)
                self.gpt_response_frame.delete('1.0', tk.END)
                self.gpt_response_frame.insert("1.0", s)


    def load_model_callback(self):
        path = filedialog.askdirectory(title="Load experiment")
        if path:
            self.dp.dprint("ModelExplorer.load_model_callback() loading {}".format(path))
            self.hgpt = HFaceGPT(path)
            self.calc_percents()
            self.dp.dprint("ModelExplorer.load_model_callback() loaded {}".format(path))

    def setup(self):
        self.dp.dprint("pre-running setup")

def main():
    app = ModelExplorer()
    app.setup()
    app.mainloop()

if __name__ == "__main__":
    main()