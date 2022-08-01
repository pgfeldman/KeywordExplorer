import tkinter as tk

# Modified from astqx's solution on StackOverflow: https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
class ToolTip:
    tooltip:tk.Toplevel
    x_offset:int
    y_offset:int

    def __init__(self,widget,text:str=None, xoff:int=15, yoff:int=10):
        self.widget=widget
        self.text=text
        self.x_offset = xoff
        self.y_offset = yoff

        self.widget.bind('<Enter>',self.on_enter)
        self.widget.bind('<Leave>',self.on_leave)

    def on_enter(self, event):
        self.tooltip=tk.Toplevel()
        self.tooltip.overrideredirect(True)
        self.tooltip.geometry(f'+{event.x_root+self.x_offset}+{event.y_root+self.y_offset}')

        self.label=tk.Label(self.tooltip,text=self.text, borderwidth=1, relief="solid", justify=tk.LEFT)
        self.label.configure(background="yellow")
        self.label.pack()

    def on_leave(self, event):
        self.tooltip.destroy()