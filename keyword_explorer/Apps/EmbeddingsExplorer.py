import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as message
from datetime import datetime, timedelta
from tkinter import filedialog

from keyword_explorer.Apps.AppBase import AppBase
from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms
from keyword_explorer.tkUtils.CanvasFrame import CanvasFrame
from keyword_explorer.utils.MySqlInterface import MySqlInterface

class EmbeddingsExplorer(AppBase):
    oai:OpenAIComms

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("EmbeddingsExplorer")

    def setup_app(self):
        self.app_name = "EmbeddingsExplorer"
        self.app_version = "8.26.22"
        self.geom = (600, 500)
        self.oai = OpenAIComms()

        if not self.oai.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'OPENAI_KEY'")

    def build_app_view(self, row:int, text_width:int, label_width:int) -> int:
        print("build_app_view")
        s = ttk.Style()
        s.configure('TNotebook.Tab', font=self.default_font)

        # Add the tabs
        tab_control = ttk.Notebook(self)
        tab_control.grid(column=0, row=row, columnspan=2, sticky="nsew")
        json_tab = ttk.Frame(tab_control)
        tab_control.add(json_tab, text='Get/Store')

        canvas_tab = ttk.Frame(tab_control)
        tab_control.add(canvas_tab, text='Canvas')
        self.build_graph_tab(canvas_tab)
        row += 1

    def build_graph_tab(self, tab:ttk.Frame):
        row = 0
        self.canvas_frame = CanvasFrame(tab, row, "Graph", self.dp, width=550, height=250)

def main():
    app = EmbeddingsExplorer()
    app.mainloop()

if __name__ == "__main__":
    main()