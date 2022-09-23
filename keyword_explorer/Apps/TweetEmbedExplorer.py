import re
import tkinter.messagebox as message
import tkinter as tk
from tkinter import ttk
from matplotlib import pyplot as plt

from keyword_explorer.Apps.AppBase import AppBase
from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms
from keyword_explorer.tkUtils.CanvasFrame import CanvasFrame
from keyword_explorer.tkUtils.TopicComboExt import TopicComboExt
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.LabeledParam import LabeledParam
from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.ToolTip import ToolTip
from keyword_explorer.utils.MySqlInterface import MySqlInterface
from keyword_explorer.utils.ManifoldReduction import ManifoldReduction

from typing import Dict

# General TODO:
# Move "selected experiment" and "keyword" out of the tabs
# Add a "Create Corpora" tab
# Implement calls to GPT embeddings and verify on small dataset. I could even try Aaron's Wikipedia cats vs computers idea but use tweets
class EmbeddingsExplorer(AppBase):
    oai: OpenAIComms
    msi: MySqlInterface
    canvas_frame: CanvasFrame
    engine_combo: TopicComboExt
    keyword_combo: TopicComboExt
    graph_keyword_combo: TopicComboExt
    experiment_combo: TopicComboExt
    keyword_count_field: DataField
    pca_dim_param: LabeledParam
    eps_param: LabeledParam
    min_samples_param: LabeledParam
    perplexity_param: LabeledParam
    experiment_id: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("EmbeddingsExplorer")

    def setup_app(self):
        self.app_name = "EmbeddingsExplorer"
        self.app_version = "9.9.22"
        self.geom = (600, 620)
        self.oai = OpenAIComms()
        self.msi = MySqlInterface(user_name="root", db_name="twitter_v2")

        if not self.oai.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'OPENAI_KEY'")
        self.experiment_id = -1


    def build_app_view(self, row: int, text_width: int, label_width: int) -> int:
        experiments = ["exp_1", "exp_2", "exp_3"]
        keywords = ["foo", "bar", "bas"]
        print("build_app_view")

        self.experiment_combo = TopicComboExt(self, row, "Experiment:", self.dp, entry_width=20, combo_width=20)
        self.experiment_combo.set_combo_list(experiments)
        self.experiment_combo.set_callback(self.keyword_callback)
        row = self.experiment_combo.get_next_row()
        self.keyword_combo = TopicComboExt(self, row, "Keyword:", self.dp, entry_width=20, combo_width=20)
        self.keyword_combo.set_combo_list(keywords)
        b = self.keyword_combo.add_button("Num Entries:", command=lambda: self.get_keyword_entries_callback(
            self.keyword_combo.get_text()))
        ToolTip(b, "Query the DB to see how many entries there are\nResults go in 'Num Rows:'")
        row = self.keyword_combo.get_next_row()

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

        corpora_tab = ttk.Frame(tab_control)
        tab_control.add(corpora_tab, text='Corpora')
        self.build_create_corpora_tab(corpora_tab)
        row += 1

        return row

    def build_create_corpora_tab(self, tab: ttk.Frame):
        pass

    def build_get_store_tab(self, tab: ttk.Frame):
        engine_list = ['text-similarity-ada-001',
                       'text-similarity-babbage-001',
                       'text-similarity-curie-001',
                       'text-similarity-davinci-001']
        row = 0
        self.engine_combo = TopicComboExt(tab, row, "Engine:", self.dp, entry_width=20, combo_width=20)
        self.engine_combo.set_combo_list(engine_list)
        self.engine_combo.set_text(engine_list[0])
        self.engine_combo.tk_combo.current(0)
        row = self.engine_combo.get_next_row()
        self.keyword_count_field = DataField(tab, row, "Num rows")
        self.keyword_count_field.add_button("Get Embeddings", self.get_oai_embeddings_callback)
        row = self.keyword_count_field.get_next_row()

    def build_param_row(self, parent:tk.Frame, row:int) -> int:
        f = tk.Frame(parent)
        f.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=1, pady=1)
        self.pca_dim_param = LabeledParam(f, 0, "PCA Dim:")
        self.pca_dim_param.set_text('10')
        self.eps_param = LabeledParam(f, 2, "EPS:")
        self.eps_param.set_text('8')
        self.min_samples_param = LabeledParam(f, 4, "Min Samples:")
        self.min_samples_param.set_text('5')
        self.perplexity_param = LabeledParam(f, 6, "Perplex:")
        self.perplexity_param.set_text('80')
        return row + 1

    def build_graph_tab(self, tab: ttk.Frame):
        row = 0
        row = self.build_param_row(tab, row)
        f = tk.Frame(tab)
        # add "select clusters" field and "export corpus" button
        buttons = Buttons(tab, row, "Commands", label_width=10)
        b = buttons.add_button("Retreive", self.get_db_embeddings_callback)
        ToolTip(b, "Get the high-dimensional embeddings from the DB")
        b = buttons.add_button("Reduce", self.implement_me)
        b = buttons.add_button("Cluster", self.implement_me)
        ToolTip(b, "Set the projection and cluster data")
        b = buttons.add_button("PyPlot", self.implement_me)
        b = buttons.add_button("Label topics", self.implement_me)
        row = buttons.get_next_row()

        f = tk.Frame(tab)
        f.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=1, pady=1)
        row = 0
        self.canvas_frame = CanvasFrame(f, row, "Graph", self.dp, width=550, height=250)

    def get_db_embeddings_callback(self):
        print("get_db_embeddings_callback")
        keyword = self.keyword_combo.get_text()

        if self.experiment_id == -1 or len(keyword) < 2:
            message.showwarning("DB Error", "get_db_embeddings_callback(): Please set database and/or keyword")
            return

        query = "select tweet_id, embedding from keyword_tweet_view where experiment_id = %s"
        values = (self.experiment_id,)
        if keyword != 'all_keywords':
            query = "select tweet_id, embedding from keyword_tweet_view where experiment_id = %s and keyword = %s"
            values = (self.experiment_id, keyword)
        result = self.msi.read_data(query, values, True)
        row_dict:Dict

        mr:ManifoldReduction = ManifoldReduction(2)
        print("Loading {} rows".format(len(result)))
        for row_dict in result:
            mr.load_row(row_dict['embedding'])

        fig, axs = plt.subplots(1, 1)
        pca_dim = self.pca_dim_param.get_as_int()
        eps = self.eps_param.get_as_int()
        min_namples = self.min_samples_param.get_as_int()
        perplexity = self.perplexity_param.get_as_int()

        print("Calculating  perplexity = {}".format(perplexity))
        mr.calc_embeding(perplexity=perplexity, pca_components=pca_dim)
        mr.dbscan(eps=eps, min_samples=min_namples)

        print("Plotting")
        mr.plot("perplex = {}".format(perplexity))
        plt.show()

    def get_oai_embeddings_callback(self):
        print("get_oai_embeddings_callback")
        keyword = self.keyword_combo.get_text()

        if self.experiment_id == -1 or len(keyword) < 2:
            message.showwarning("DB Error", "get_oai_embeddings_callback(): Please set database and/or keyword")
            return

        query = "select tweet_id, text from keyword_tweet_view where experiment_id = %s and embedding is NULL"
        values = (self.experiment_id,)
        if keyword != 'all_keywords':
            query = "select tweet_id, text from keyword_tweet_view where experiment_id = %s and keyword = %s and embedding is NULL"
            values = (self.experiment_id, keyword)

        engine = self.engine_combo.get_text()
        print("get_embeddings_callback() Experiment id = {}, Keyword = {}, Engine = {}".format(self.experiment_id, keyword, engine))
        result = self.msi.read_data(query, values)
        row_dict:Dict
        for row_dict in result:
            id = row_dict['tweet_id']
            tweet = row_dict['text']
            embd = self.oai.get_embedding(tweet, engine)
            print("id: {} text: {} embed: {}".format(id, tweet, embd))
            query = "update table_tweet set embedding = %s where id = %s"
            values = ("{}:{}".format(engine, embd), id)
            self.msi.write_sql_values_get_row(query, values)


    def get_keyword_entries_callback(self, keyword: str):
        print("get_keyword_entries: keyword = {}, experiment_id = {}".format(keyword, self.experiment_id))
        query = "select count(*) from keyword_tweet_view where experiment_id = %s"
        values = (self.experiment_id)
        if keyword != 'all_keywords':
            query = "select count(*) from keyword_tweet_view where experiment_id = %s and keyword = %s"
            values = (self.experiment_id, keyword)
        result:Dict = self.msi.read_data(query, values)[0]
        count = result['count(*)']

        self.keyword_count_field.set_text(count)

    def keyword_callback(self, event:tk.Event):
        print("keyword_callback: event = {}".format(event))
        num_regex = re.compile(r"\d+")
        s = self.experiment_combo.tk_combo.get()
        self.experiment_combo.set_text(s)
        self.experiment_id = num_regex.findall(s)[0]
        print("keyword_callback: experiment_id = {}".format(self.experiment_id))
        query = "select distinct keyword from table_query where experiment_id = %s"
        values = (self.experiment_id,)
        result = self.msi.read_data(query, values)
        l = ['all_keywords']
        row_dict:Dict
        for row_dict in result:
            l.append(row_dict['keyword'])
        self.keyword_combo.set_combo_list(l)


    def setup(self):
        # set up the canvas
        self.canvas_frame.setup(debug=True, show_names=False)

        # set up the selections that come from the db
        l = []
        row_dict:Dict
        query = "select * from table_experiment"
        result = self.msi.read_data(query)
        for row_dict in result:
            s = "{}: {}".format(row_dict['id'], row_dict['keywords'])
            l.append(s)
        self.experiment_combo.set_combo_list(l)


def main():
    app = EmbeddingsExplorer()
    app.setup()
    app.mainloop()


if __name__ == "__main__":
    main()
