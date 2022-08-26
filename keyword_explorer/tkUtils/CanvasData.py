import tkinter as tk

class CanvasData:
    left:int
    top:int
    right:int
    bottom:int
    center_x:int
    center_y:int
    canvas:tk.Canvas

    def __init__(self, canvas:tk.Canvas):
        self.canvas = canvas
        self.left = 0
        self.top = 0
        self.right = self.canvas.winfo_width()
        self.bottom = self.canvas.winfo_height()
        self.center_x = self.right // 2
        self.center_y = self.bottom // 2