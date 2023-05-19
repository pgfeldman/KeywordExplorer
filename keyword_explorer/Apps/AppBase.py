import getpass
import inspect
import re
import tkinter as tk
from tkinter import filedialog
from tkinter.font import Font
from datetime import datetime
from pathlib import Path
import json
from typing import Tuple, Dict, List, Any

from keyword_explorer.tkUtils.ConsoleDprint import ConsoleDprint
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.utils.SharedObjects import SharedObjects
from keyword_explorer.tkUtils.ToolTip import ToolTip


class AppBase(tk.Tk):
    experiment_field:DataField
    logfile:str
    app_name:str
    app_version:str
    app_geom:Tuple
    dp:ConsoleDprint
    so:SharedObjects
    console_lines:int
    text_width:int
    label_width:int
    default_font:Font

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_font = Font(family='courier', size = 10)
        self.console_lines = 5
        self.text_width = 53
        self.label_width = 15
        self.so = SharedObjects()
        self.dp = ConsoleDprint()
        self.setup_app()
        self.build_view()
        self.dp.dprint("{} is running!".format(self.app_name))
        dt = datetime.now()
        self.logfile = "{}/{}_{}.csv".format(Path.home(), self.app_name, dt.strftime("%Y-%m-%d-%H-%M-%S"))
        self.log_action("session", {"session start":dt.strftime("%H:%M:%S")})


    def setup_app(self):
        self.app_name = "AppBase"
        self.app_version = "1.27.2023"
        self.geom = (600, 150)


    def build_view(self):
        row = 0

        self.title("{} (v {})".format(self.app_name, self.app_version))
        self.geometry("{}x{}".format(self.geom[0], self.geom[1]))
        self.resizable(width=True, height=False)

        self.experiment_field = DataField(self, row, "Experiment name:", self.text_width, label_width=self.label_width)
        tt = ToolTip(self.experiment_field.tk_entry, "The name of the project\nUsed for file names and\ndatabase fields")
        dt = datetime.now()
        self.logfile = "{}/{}_{}.csv".format(Path.home(), self.app_name, dt.strftime("%Y-%m-%d-%H-%M-%S"))
        experiment_str = "{}_{}_{}".format(getpass.getuser(), self.app_name, dt.strftime("%Y-%m-%d-%H-%M-%S"))
        self.experiment_field.set_text(experiment_str)
        row = self.experiment_field.get_next_row()

        row = self.build_app_view(row, self.text_width, self.label_width)

        self.dp.create_tk_console(self, row=row, height=self.console_lines, char_width=self.text_width+self.label_width, set_console=True)
        self.build_menus()

    def build_app_view(self, row:int, text_width:int, label_width:int) -> int:
        return row

    def build_menus(self):
        print("building menus")
        self.option_add('*tearOff', tk.FALSE)
        menubar = tk.Menu(self)
        self['menu'] = menubar
        menu_file = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='Load experiment', command=self.load_experiment_callback)
        menu_file.add_command(label='Save experiment', command=self.save_experiment_callback)
        menu_file.add_command(label='Load IDs', command=self.load_ids_callback)
        menu_file.add_command(label='Exit', command=self.terminate)

    def load_json(self, key_dict:Dict) -> Dict:
        so = SharedObjects()
        result = filedialog.askopenfile(filetypes=(("JSON files", "*.json"),("All Files", "*.*")), title="Load json ID file")
        if result:
            so.load_from_file(result.name)
            for key in key_dict.keys():
                val = so.get_object(key)
                if val != None:
                    key_dict[key] = val
        return key_dict

    def load_ids_callback(self):
        result = filedialog.askopenfile(filetypes=(("JSON files", "*.json"),("All Files", "*.*")), title="Load json ID file")
        if result:
            self.so.load_from_file(result.name)
            self.tvc.bearer_token = self.so.get_object('BEARER_TOKEN_2')
            #print("bearer_token = {}".format(self.tvc.bearer_token))

    # override to do app-specific stuff
    def set_experiment_text(self, l:List):
        for s in l:
            self.dp.dprint(s)

    def load_experiment_callback(self):
        result = filedialog.askopenfile(filetypes=(("Text files", "*.txt"),("All Files", "*.*")), title="Load experiment")
        l = []
        if result:
            filename = result.name
            self.dp.dprint("AppBase.load_experiment_callback() loading {}".format(filename))
            with open(filename, encoding="utf8") as f:
                for line in f:
                    if len(line) > 1:
                        l.append(line.strip())
        self.set_experiment_text(l)

    def save_experiment_text(self, filename:str):
        l = ["one", "two", "three"]
        with open(filename, mode="w", encoding="utf8") as f:
            for line in l:
                f.write(line+"\n")

    def save_experiment_callback(self):
        result = filedialog.asksaveasfile(filetypes=(("Text files", "*.txt"),("All Files", "*.*")), title="Save/Update experiment")
        l = []
        if result:
            filename = result.name
            print("AppBase.save_experiment_callback() Saving to {}".format(filename))
            self.save_experiment_text(filename)

    def save_experiment_json(self, d:Dict):
        result = filedialog.asksaveasfile(filetypes=(("JSON files", "*.json"),("All Files", "*.*")), title="Save/Update experiment")
        if result:
            filename = result.name
            print("AppBase.save_experiment_json() Saving to {}".format(filename))
            with open (filename, 'w') as f:
                json.dump(d, f, indent=4)

    def safe_dict_read(self, d:Dict, key:str, default:Any) -> Any:
        if key in d and d[key] != None:
            return d[key]
        return default

    def clean_text(self, s:str) -> str:
        char_list = [s[j] for j in range(len(s)) if ord(s[j]) in range(65536)]
        s=''
        for j in char_list:
            s=s+j
        return s



    def log_action(self, task:str, row_info:Dict, mode:str = "a"):
        with open(self.logfile, mode, encoding="utf-8") as fio:
            dt = datetime.now()
            ds = dt.strftime("%H:%M:%S")
            s = "time, {}, task, {}".format(ds, task)
            for key, val in row_info.items():
                if isinstance(val, str):
                    val = val.replace("\n", " ")
                s += ", {}, {}".format(key, val)
            try:
                fio.write("{}\n".format(s))
            except UnicodeEncodeError:
                print("unable to write {}".format(s))
            fio.close()

    def terminate(self):
        """
        The callback called when clicking the exit button
        :return:
        """
        print("terminating")
        self.destroy()

    def implement_me(self, event:tk.Event = None):
        """
        A callback to point to when you you don't have a method ready. Prints "implement me!" to the output and
        an abbreviated version of the call stack to the console
        :return:
        """
        #self.dprint("Implement me!")
        self.dp.dprint("Implement me! (see console for call stack)")
        fi:inspect.FrameInfo
        count = 0
        self.dp.dprint("\nImplement me!")
        for fi in inspect.stack():
            filename = re.split(r"(/)|(\\)", fi.filename)
            print("Call stack[{}] = {}() (line {} in {})".format(count, fi.function, fi.lineno, filename[-1]))

def main():
    app = AppBase()
    app.mainloop()

if __name__ == "__main__":
    # print(Path.home())
    main()