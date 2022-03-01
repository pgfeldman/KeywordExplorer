import random
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Tuple, Any, Union, Callable

from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.TextField import TextField
from keyword_explorer.tkUtils.TopicCombo import TopicCombo
from keyword_explorer.utils.TextSimilarity import TextSimilarity

class TextCompareData:
    new_text:str
    title:str
    rank:float
    content:str
    data:Any
    meta:Union[None, str]

    def __init__(self, title:str, d:Dict):
        self.title = title
        self.rank = self.set_val(d, 'rank')
        self.content = self.set_val(d, 'content')
        self.meta = self.set_val(d, 'meta')
        self.data = self.set_val(d, 'data')
        self.new_text = self.set_val(d, 'new_text')

    def set_val(self, d:Dict, key:str) -> Any:
        if key in d:
            return d[key]
        return None

    def get_new_text(self) ->str:
        return self.new_text

    def get_label(self) -> str:
        return "({:.2f}) {}".format(self.rank, self.title)

    def get_title(self) -> str:
        return self.title

    def get_content(self) -> str:
        if self.meta != None:
            return "{}:\nrank: {:.1f}%\n{}".format(self.meta, (self.rank*100), self.content)
        return "rank: {:.1f}%\n{}".format((self.rank*100), self.content)

    def get_data(self) -> Any:
        return self.data

    def to_string(self) -> str:
        return "Title: {}, Rank: {:.2f}, Compare: {}".format(self.get_title(), self.rank, self.new_text)



class TextComparePopup:
    win:tk.Toplevel
    new_text_field:TextField
    select_best_combo:TopicCombo
    candidate_text:TextField
    option_buttons:Buttons
    content_list:List[TextCompareData]
    selected_tcd:Union[TextCompareData, None]
    selected_callback:Union[Callable, None]
    exit_callback:Union[Callable, None]

    def __init__(self):
        self.build_view()
        self.selected_callback = None
        self.exit_callback = None
        self.reset()

    def reset(self):
        self.selected_tcd = None
        self.content_list = []

    def build_view(self):
        row = 0
        self.win = tk.Toplevel()
        self.win.wm_title("Text Compare")
        self.win.geometry("530x320")
        self.win.resizable(width=False, height=False)

        self.win.protocol("WM_DELETE_WINDOW", self.terminate)

        f:tk.Frame = tk.Frame(self.win)
        f.grid(row=row, sticky="nsew")

        text_width = 45
        row = 0
        self.new_text_field = TextField(f, row, 'New text', text_width, label_width=15, height=7)
        row = self.new_text_field.get_next_row()

        self.select_best_combo = TopicCombo(f, row, "Options", button_label="Select")
        self.select_best_combo.set_button_callback(self.on_selected_text_button_clicked)
        self.select_best_combo.set_combo_callback(self.on_selected_text_dropdown_selected)
        row = self.select_best_combo.get_next_row()

        self.candidate_text = TextField(f, row, 'Candidate Match:', text_width, label_width=15, height=7)
        row = self.candidate_text.get_next_row()

        buttons = Buttons(f, row, "Options")
        buttons.add_button("Exit", self.terminate)
        row = buttons.get_next_row()

    def set_selected_callback(self, cb:Callable):
        self.selected_callback = cb

    def on_selected_text_button_clicked(self):
        if self.selected_callback != None:
            self.selected_callback(self.selected_tcd)
        else:
            print("TextComparePopup.on_selected_text_button_clicked(): {}".format(self.selected_tcd.to_string()))

    def on_selected_text_dropdown_selected(self, event:tk.Event):
        tkl:ttk.Combobox = event.widget
        label:str = tkl.get().replace("...", "")
        tcd:TextCompareData
        for tcd in self.content_list:
            #print("testing if {} is in {}".format(label, tcd.get_label()))
            if label in tcd.get_label():
                self.candidate_text.set_text(tcd.get_content())
                self.selected_tcd = tcd
                break
        #print("on_selected_text_dropdown_selected(): implement me!")

    # sort function based on rank
    def keyfunk(self, tup):
        key, d = tup
        return d["rank"]

    def set_data(self, label:str, d:Dict):
        self.reset()
        self.new_text_field.set_text(label)
        l:List = sorted(d.items(), key = self.keyfunk, reverse=True)
        entry:Dict
        t:Tuple
        self.select_best_combo.clear_combo()
        for t in l:
            entry = t[1]
            entry['new_text'] = label
            tcd = TextCompareData(t[0], entry)
            self.select_best_combo.add_to_combo_list(tcd.get_label())
            self.content_list.append(tcd)
        self.select_best_combo.set_combo_index(0)

    def set_exit_callback(self, cb:Callable):
        self.exit_callback = cb

    def terminate(self):
        if self.exit_callback != None:
            self.exit_callback()
        else:
            print("terminating")
            self.win.destroy()

# make some fake data for testing. Note that the compare is done BEFORE loading the
# widget.
def make_data(master:str, text_list:List[str], meta_list:List) -> Dict:
    ts = TextSimilarity()
    d = {}
    for t in text_list:
        name = t
        rank = ts.compare_two_texts(master, t)
        dc = {"rank":rank, "content":name, "meta":random.choice(meta_list)}
        d[name] = dc
    return d

if __name__ == "__main__":
    text_list = ["The Moon landing was a hoax.",
            "The US government staged the Moon landing to impress the world and scare the Soviets.",
            "The US government staged the Moon landing to take over the world.",
            "The first Moon landing never happened; it was filmed in a Hollywood studio.",
            "Recent lunar missions never landed on the Moon; they were filmed in a Hollywood studio.",
            "A group of scientists arranged for the first televised broadcast of people walking on the Moon to be faked.",
            "Stanley Kubrick arranged for the first televised broadcast of people walking on the Moon to be faked.",
            "9/11 was an inside job.",
            "Bush planned and carried out 9/11, or Bush knew about the attacks but did nothing to stop them.",
            "The government is incarcerating American citizens in FEMA concentration camps.",
            "World War II never happened.",
            "Obama faked his birth certificate.",
            "Vaccines cause autism."]
    meta_list = ["Group AAA", "Group BBB", "Group CCC", "Group DDD", "Group EEE", "Group FFF"]
    random.shuffle(text_list)
    content = text_list.pop()
    tcp = TextComparePopup()
    d = make_data(content, text_list, meta_list)
    tcp.set_data(content, d)
    root = tk.Tk()
    root.mainloop()