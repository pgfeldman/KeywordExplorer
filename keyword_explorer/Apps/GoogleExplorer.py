from tkinterweb import HtmlFrame #import the HTML browser
import tkinter as tk
import tkinter.messagebox as message
import os
import webbrowser


from keyword_explorer.Apps.AppBase import AppBase
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.Buttons import Buttons
from keyword_explorer.tkUtils.ToolTip import ToolTip
import keyword_explorer.utils.google_search as gs

html_str = '''<!DOCTYPE html>
    <html>
        <head>
            <title>Example</title>
        </head>
        <body>
            <p>This <a href="https://philfeldman.com/resume.html">link</a> points to my resume</p>
        </body>
    </html>'''

html_begin = '''<!DOCTYPE html>
    <html>
        <head>
            <title>Example</title>
        </head>
        <body>
        '''

html_end = html_str = '''
        </body>
    </html>'''

class GoogleExplorer(AppBase):
    search_field:DataField
    search_frame:HtmlFrame
    action_buttons:Buttons

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("GoogleExplorer")

    def setup_app(self):
        self.app_name = "GoogleExplorer"
        self.app_version = "4.11.2023"
        self.geom = (850, 850)
        if not gs.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'GOOGLE_CSE_KEY'")

    def build_app_view(self, row:int, text_width:int, label_width:int) -> int:
        row += 1
        lf = tk.LabelFrame(self, text="Search")
        lf.grid(row=row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_search(lf, text_width, label_width)

    def build_search(self, parent:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.search_field = DataField(parent, row, "Search:", text_width, label_width=label_width)
        ToolTip(self.search_field.tk_entry, "Type your search term or phrase here")
        row = self.search_field.get_next_row()

        self.action_buttons = Buttons(parent, row, "Actions:", label_width)
        self.action_buttons.add_button("Search", self.search_callback)
        row = self.action_buttons.get_next_row()


        self.search_frame = HtmlFrame(parent) #create HTML browser
        self.search_frame.load_html(html_str)
        self.search_frame.on_link_click(self.load_new_page)
        self.search_frame.grid(row = row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
        ToolTip(self.search_frame, "Search results are here\nLinks open tabs in your default browser")

    def search_callback(self):
        query = self.search_field.get_text()
        engine = gs.engines['com-org-edu']
        key = os.environ.get("GOOGLE_CSE_KEY")
        if key == None:
            key = self.so.get_object("GOOGLE_CSE_KEY")
        if key == None:
            message.showwarning("Key Error", "Could not find Environment key 'GOOGLE_CSE_KEY. Please load from ids.json file'")
            return

        self.log_action("search", {"query":query})
        results_list, info_list = gs.get_search_results_list(query, engine, key)
        s = html_begin
        g:gs.GoogleCSEResult
        for g in results_list:
            s += g.to_html()
            # print("\n{}".format(g.to_string()))
        s += html_end
        self.search_frame.load_html(s)

    def load_new_page(self, url):
        print(url)
        self.log_action("load_new_page", {"clicked":url})
        webbrowser.open(url)
        # self.search_frame.load_url(url)

def example_main():
    root = tk.Tk() #create the tkinter window
    frame = HtmlFrame(root) #create HTML browser

    #frame.load_website("http://tkhtml.tcl.tk/tkhtml.html") #load a website
    frame.load_html(html_str) #load a website
    frame.pack(fill="both", expand=True) #attach the HtmlFrame widget to the parent window
    root.mainloop()

def main():
    print("Hello GoogleExplorer: {}".format(os.getcwd()))
    app = GoogleExplorer()
    app.mainloop()

if __name__ == "__main__":
    main()