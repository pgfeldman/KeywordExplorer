import tkinter as tk
from tkinter import ttk
import tkinter.font as tkf
import textwrap

class ConsoleDprint:
    main_console:tk.Text
    dcount:int = 0
    def __init__(self, console:tk.Text = None):
        self.set_console(console)

    def set_console(self, console:tk.Text = None):
        self.main_console = console

    def dprint(self, text: str, max_chars:int = -1):
        if self.main_console:
            if max_chars > -1:
                text = textwrap.shorten(text, width=max_chars)

            self.main_console.insert("1.0", "[{}] {}\n".format(self.dcount, text))
            # self.main_console.set_text(text, self.dcount)
            self.dcount += 1
            self.main_console.update()
        else:
            print(text)

    def create_tk_console(self, parent, row:int, height:int = 5, char_width:int = 100, set_console:bool = True) -> tk.Text:
        console_wrapper = tk.LabelFrame(parent, text="Console")
        main_console = tk.Text(console_wrapper, width=char_width, height=height, wrap=tk.WORD, borderwidth=2, relief="groove")
        console_wrapper.grid(row=row, column=0, columnspan = 2, sticky="nsew", padx=5, pady=2)
        text_scrollbar = ttk.Scrollbar(console_wrapper, orient=tk.VERTICAL, command=main_console.yview)
        main_console['yscrollcommand'] = text_scrollbar.set
        main_console.grid(column=0, row=0, rowspan=1, sticky="nsew", padx=5, pady=2)
        text_scrollbar.grid(column=1, row=0, rowspan=1, sticky=(tk.N, tk.S))

        if set_console:
            self.main_console = main_console

        return main_console

if __name__ == "__main__":
    cp = ConsoleDprint()
    print("Hello, ConsoleDprint")

