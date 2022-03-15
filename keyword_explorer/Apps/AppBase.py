import getpass
import inspect
import re
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from typing import Tuple, Dict, IO

from keyword_explorer.tkUtils.ConsoleDprint import ConsoleDprint
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.utils.SharedObjects import SharedObjects


class AppBase(tk.Tk):
    experiment_field:DataField
    logfile:str
    app_name:str
    app_version:str
    app_geom:Tuple
    dp:ConsoleDprint
    so:SharedObjects

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.so = SharedObjects()
        self.dp = ConsoleDprint()
        self.setup_app()
        self.build_view()
        self.dp.dprint("{} is running!".format(self.app_name))
        dt = datetime.now()
        self.logfile = "../../data/{}_{}.csv".format(self.app_name, dt.strftime("%Y-%m-%d-%H-%M-%S"))
        self.log_action("session", {"session start":dt.strftime("%H:%M:%S")})

    def setup_app(self):
        self.app_name = "AppBase"
        self.app_version = "3.10.2022"
        self.geom = (600, 150)

    def build_view(self):
        text_width = 53
        label_width = 15
        row = 0

        self.title("{} (v {})".format(self.app_name, self.app_version))
        self.geometry("{}x{}".format(self.geom[0], self.geom[1]))
        self.resizable(width=True, height=False)

        self.experiment_field = DataField(self, row, "Experiment name:", text_width, label_width=label_width)
        self.experiment_field.set_text(getpass.getuser())
        row = self.experiment_field.get_next_row()

        row = self.build_app_view(row, text_width, label_width)

        self.dp.create_tk_console(self, row=row, height=5, char_width=text_width+label_width, set_console=True)
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
        menu_file.add_command(label='Load IDs', command=self.load_ids_callback)
        menu_file.add_command(label='Exit', command=self.terminate)

    def load_ids_callback(self):
        result = filedialog.askopenfile(filetypes=(("JSON files", "*.json"),("All Files", "*.*")), title="Load json ID file")
        if result:
            self.so.load_from_file(result.name)
            self.tvc.bearer_token = self.so.get_object('BEARER_TOKEN_2')
            print("bearer_token = {}".format(self.tvc.bearer_token))

    def log_action(self, task:str, row_info:Dict, mode:str = "a"):
        with open(self.logfile, mode) as fio:
            dt = datetime.now()
            ds = dt.strftime("%H:%M:%S")
            s = "time, {}, task, {}".format(ds, task)
            for key, val in row_info.items():
                if isinstance(val, str):
                    val = val.replace("\n", " ")
                s += ", {}, {}".format(key, val)
            fio.write("{}\n".format(s))
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
    main()