from tkinterweb import HtmlFrame #import the HTML browser
import tkinter as tk
import tkinter.messagebox as message
import os
import webbrowser


from keyword_explorer.Apps.AppBase import AppBase
from keyword_explorer.tkUtils.DataField import DataField
from keyword_explorer.tkUtils.Buttons import Buttons
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("GoogleExplorer")

    def setup_app(self):
        self.app_name = "GoogleExplorer"
        self.app_version = "3.14.22"
        self.geom = (850, 850)
        if not gs.key_exists():
            message.showwarning("Key Error", "Could not find Environment key 'GOOGLE_CSE_KEY'")

    def build_app_view(self, row:int, text_width:int, label_width:int) -> int:
        row += 1
        lf = tk.LabelFrame(self, text="Search")
        lf.grid(row=row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
        self.build_search(lf, text_width, label_width)


        #frame.pack(fill="both", expand=True)

    def build_search(self, parent:tk.LabelFrame, text_width:int, label_width:int):
        row = 0
        self.search_field = DataField(parent, row, "Search:", text_width, label_width=label_width)
        row = self.search_field.get_next_row()

        buttons = Buttons(parent, row, "Actions:", label_width)
        buttons.add_button("Search", self.search_callback)
        row = buttons.get_next_row()


        self.search_frame = HtmlFrame(parent) #create HTML browser
        self.search_frame.load_html(html_str)
        self.search_frame.on_link_click(self.load_new_page)
        self.search_frame.grid(row = row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)

    def search_callback(self):
        query = self.search_field.get_text()
        engine = gs.engines['all.com']
        key = os.environ.get("GOOGLE_CSE_KEY")
        if key == None:
            key = self.so.get_object("GOOGLE_CSE_KEY")
        if key == None:
            message.showwarning("Key Error", "Could not find Environment key 'GOOGLE_CSE_KEY. Please load from ids.json file'")
            return

        l = gs.get_search_results_list(query, engine, key)
        s = html_begin
        g:gs.GoogleCSEResult
        for g in l:
            s += g.to_html()
            print("\n{}".format(g.to_string()))
        s += html_end
        self.search_frame.load_html(s)

    def load_new_page(self, url):
        print(url)
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
    print("GoogleExplorer")
    app = GoogleExplorer()
    app.mainloop()

if __name__ == "__main__":
    main()