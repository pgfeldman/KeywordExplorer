import tkinter.messagebox as message
import tkinter as tk
from tkinter import ttk

from keyword_explorer.Apps.AppBase import AppBase
from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms
from keyword_explorer.tkUtils.CanvasFrame import CanvasFrame
from keyword_explorer.tkUtils.TopicComboExt import TopicComboExt
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.utils.MySqlInterface import MySqlInterface


class EmbeddingsExplorer(AppBase):
    oai: OpenAIComms
    msi: MySqlInterface
    canvas_frame: CanvasFrame
    engine_combo: TopicComboExt
    keyword_combo: TopicComboExt
    keyword_count_field: DataField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("EmbeddingsExplorer")

    def setup_app(self):
        self.app_name = "EmbeddingsExplorer"
        self.app_version = "8.26.22"
        self.geom = (600, 600)
        self.oai = OpenAIComms()
        self.msi = MySqlInterface(user_name ="root", db_name ="twitter_v2")

        if not self.oai.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'OPENAI_KEY'")

    def build_app_view(self, row: int, text_width: int, label_width: int) -> int:
        print("build_app_view")
        s = ttk.Style()
        s.configure('TNotebook.Tab', font=self.default_font)

        # Add the tabs
        tab_control = ttk.Notebook(self)
        tab_control.grid(column=0, row=row, columnspan=2, sticky="nsew")
        get_store_tab = ttk.Frame(tab_control)
        tab_control.add(get_store_tab, text='Get/Store')
        self.build_get_store_tab(get_store_tab)

        canvas_tab = ttk.Frame(tab_control)
        tab_control.add(canvas_tab, text='Canvas')
        self.build_graph_tab(canvas_tab)
        row += 1

        return row

    def get_keyword_entries(self, keyword: str):
        print("get_keyword_entries: {}".format(keyword))
        self.keyword_count_field.set_text("12345")

    def get_embeddings(self):
        print("get_embeddings")

    def build_get_store_tab(self, tab: ttk.Frame):
        engine_list = ['text-similarity-ada-001',
                       'text-similarity-babbage-001',
                       'text-similarity-curie-001',
                       'text-similarity-davinci-001']
        row = 0
        self.engine_combo = TopicComboExt(tab, row, "engine", self.dp, entry_width=20, combo_width=20)
        self.engine_combo.set_combo_list(engine_list)
        self.engine_combo.set_text(engine_list[0])
        row = self.engine_combo.get_next_row()
        self.keyword_combo = TopicComboExt(tab, row, "keyword", self.dp, entry_width=20, combo_width=20)
        self.keyword_combo.set_combo_list(["foo", "bar", "baz"])
        b = self.keyword_combo.add_button("Num Entries", command= lambda: self.get_keyword_entries(self.keyword_combo.get_text()))
        row =self.keyword_combo.get_next_row()
        self.keyword_count_field = DataField(tab, row, "Num rows")
        self.keyword_count_field.add_button("Get Embeddings", self.get_embeddings)
        row = self.keyword_count_field.get_next_row()



    def build_graph_tab(self, tab: ttk.Frame):
        row = 0
        lf = tk.LabelFrame(tab, text="Embedding Params")
        lf.grid(row=row, column=0, columnspan = 1, sticky="nsew", padx=5, pady=2)
        experiment_combo = TopicComboExt(lf, row, "Experiment:", self.dp, entry_width=20, combo_width=20)
        row = experiment_combo.get_next_row()
        keyword_combo = TopicComboExt(lf, row, "Keywords:", self.dp, entry_width=20, combo_width=20)
        row = keyword_combo.get_next_row()
        # add "select clusters" field and "export corpus" button
        cluster_size_field = DataField(lf, row, "Clusters:")
        b = cluster_size_field.add_button("Set size", self.implement_me)
        b = cluster_size_field.add_button("Label topics", self.implement_me)
        b = cluster_size_field.add_button("Update DB", self.implement_me)


        f = tk.Frame(tab)
        f.grid(row=row, column=0, columnspan = 1, sticky="nsew", padx=1, pady=1)
        row = 0
        self.canvas_frame = CanvasFrame(f, row, "Graph", self.dp, width=550, height=250)

    def setup(self):
        self.canvas_frame.setup(debug=True, show_names=False)



def main():
    app = EmbeddingsExplorer()
    app.setup()
    app.mainloop()


if __name__ == "__main__":
    main()
