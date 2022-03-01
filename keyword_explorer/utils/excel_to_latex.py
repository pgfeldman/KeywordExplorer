import pandas as pd
from tkinter import filedialog

filename = filedialog.askopenfilename(filetypes=(("XLSX files", "*.xlsx"),("All Files", "*.*")), title="Load XLSX Files")
if filename:
    print("opening {}".format(filename))

    df = pd.read_excel(filename)
    print("\\begin{table}[]\n\centering")
    print(df.to_latex())
    print("\caption{Caption}\n\label{tab:my_label}\n\end{table}")

