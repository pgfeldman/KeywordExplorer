import pandas as pd
import json
import os
import tkinter as tk
import tkinter.filedialog
from typing import Dict, List

def read_json_files_to_dataframe(directory_path:str) -> Dict[str, pd.DataFrame]:
    """
    Reads all the json files in the provided directory and places the
    values of the array labeled "experiments" into a Pandas dataframe.
    Returns a dictionary of dataframes, where the key is the filename.
    """
    dataframes = {}
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            with open(os.path.join(directory_path, filename), 'r') as file:
                json_data = json.load(file)

                # Make a summary DF
                # Create lists for rows and columns of the dataframe
                row_dict = {}

                # Iterate over the items in the dictionary
                for key, value in json_data.items():
                    if key != "experiments":
                        row_dict[key] = value

                # Create pandas dataframe
                df = pd.DataFrame.from_dict(row_dict, orient='index', columns=['Value'])
                df.index.name = 'Key'
                dataframes['Summary'] = df

                experiments = json_data['experiments']
                df = pd.DataFrame(experiments)
                dataframes[filename] = df
    return dataframes

def save_dataframes_to_excel(dataframes:Dict, output_file:str):
    # Create a Pandas Excel writer using XlsxWriter as the engine

    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

    # Loop through each dataframe and add it as a tab in the Excel file
    dataframe:pd.DataFrame
    for sheet_name, dataframe in dataframes.items():
        if sheet_name == 'Summary':
            # print("Summary = {}".format(dataframe))
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
            summary_sheet = writer.sheets[sheet_name]
            summary_sheet.write_string('A8','URL')
            summary_sheet.write_string('A9','engine')
            summary_sheet.write_string('A10','curie-instruct-beta')
            summary_sheet.write_string('A11','davinci-instruct-beta')
            summary_sheet.write_string('A12','gpt-3.5-turbo-0301')
            summary_sheet.write_string('A13','gpt-3.5-turbo')
            summary_sheet.write_string('A14','gpt-4-0314')
            summary_sheet.write_string('A15','gpt-4')
            summary_sheet.write_string('A16','text-davinci-003')
            summary_sheet.write_string('A17','TOTAL')

            summary_sheet.write_string('B9','no ctx good')
            summary_sheet.write_formula('B10', "=SUM('curie-instruct-beta'!I$2:I$36)")
            summary_sheet.write_formula('B11', "=SUM('davinci-instruct-beta'!I$2:I$36)")
            summary_sheet.write_formula('B12', "=SUM('gpt-3.5-turbo-0301'!I$2:I$36)")
            summary_sheet.write_formula('B13', "=SUM('gpt-3.5-turbo'!I$2:I$36)")
            summary_sheet.write_formula('B14', "=SUM('gpt-4-0314'!I$2:I$36)")
            summary_sheet.write_formula('B15', "=SUM('gpt-4'!I$2:I$36)")
            summary_sheet.write_formula('B16', "=SUM('text-davinci-003'!I$2:I$36)")
            summary_sheet.write_formula('B17', "=SUM(B10:B16)")

            summary_sheet.write_string('C9','no ctx bad')
            summary_sheet.write_formula('C10', "=SUM('curie-instruct-beta'!J$2:J$36)")
            summary_sheet.write_formula('C11', "=SUM('davinci-instruct-beta'!J$2:J$36)")
            summary_sheet.write_formula('C12', "=SUM('gpt-3.5-turbo-0301'!J$2:J$36)")
            summary_sheet.write_formula('C13', "=SUM('gpt-3.5-turbo'!J$2:J$36)")
            summary_sheet.write_formula('C14', "=SUM('gpt-4-0314'!J$2:J$36)")
            summary_sheet.write_formula('C15', "=SUM('gpt-4'!J$2:J$36)")
            summary_sheet.write_formula('C16', "=SUM('text-davinci-003'!J$2:J$36)")
            summary_sheet.write_formula('C17', "=SUM(C10:C16)")

            summary_sheet.write_string('D9','good/bad')
            summary_sheet.write_formula('D10', "=B10/C10")
            summary_sheet.write_formula('D11', "=B11/C11")
            summary_sheet.write_formula('D12', "=B12/C12")
            summary_sheet.write_formula('D13', "=B13/C13")
            summary_sheet.write_formula('D14', "=B14/C14")
            summary_sheet.write_formula('D15', "=B15/C15")
            summary_sheet.write_formula('D16', "=B16/C16")
            summary_sheet.write_formula('D17', "=B17/C17")

            summary_sheet.write_string('A10','engine')
            summary_sheet.write_string('A20','curie-instruct-beta')
            summary_sheet.write_string('A21','davinci-instruct-beta')
            summary_sheet.write_string('A22','gpt-3.5-turbo-0301')
            summary_sheet.write_string('A23','gpt-3.5-turbo')
            summary_sheet.write_string('A24','gpt-4-0314')
            summary_sheet.write_string('A25','gpt-4')
            summary_sheet.write_string('A26','text-davinci-003')
            summary_sheet.write_string('A27','TOTAL')

            summary_sheet.write_string('B19','ctx good')
            summary_sheet.write_formula('B20', "=SUM('curie-instruct-beta'!G$2:G$36)")
            summary_sheet.write_formula('B21', "=SUM('davinci-instruct-beta'!G$2:G$36)")
            summary_sheet.write_formula('B22', "=SUM('gpt-3.5-turbo-0301'!G$2:G$36)")
            summary_sheet.write_formula('B23', "=SUM('gpt-3.5-turbo'!G$2:G$36)")
            summary_sheet.write_formula('B24', "=SUM('gpt-4-0314'!G$2:G$36)")
            summary_sheet.write_formula('B25', "=SUM('gpt-4'!G$2:G$36)")
            summary_sheet.write_formula('B26', "=SUM('text-davinci-003'!G$2:G$36)")
            summary_sheet.write_formula('B27', "=SUM(B20:B26)")

            summary_sheet.write_string('C19','ctx bad')
            summary_sheet.write_formula('C20', "=SUM('curie-instruct-beta'!H$2:H$36)")
            summary_sheet.write_formula('C21', "=SUM('davinci-instruct-beta'!H$2:H$36)")
            summary_sheet.write_formula('C22', "=SUM('gpt-3.5-turbo-0301'!H$2:H$36)")
            summary_sheet.write_formula('C23', "=SUM('gpt-3.5-turbo'!H$2:H$36)")
            summary_sheet.write_formula('C24', "=SUM('gpt-4-0314'!H$2:H$36)")
            summary_sheet.write_formula('C25', "=SUM('gpt-4'!H$2:H$36)")
            summary_sheet.write_formula('C26', "=SUM('text-davinci-003'!H$2:H$36)")
            summary_sheet.write_formula('C27', "=SUM(C20:C26)")

        else:
            labels = sheet_name.split("_")
            sheet_name = labels[-1]
            sheet_name = sheet_name.replace(".json", "")

            dataframe.to_excel(writer, sheet_name=sheet_name[:31], index=False)

    # Save the Excel file
    writer.save()

def main():
    path = "../../data/meta_wrapping"
    # create a window
    root = tk.Tk()
    root.withdraw()

    # open the file dialog and get the selected directory
    path = tkinter.filedialog.askdirectory()

    df_dict = read_json_files_to_dataframe(path)

    name:str
    label = "unset"
    for name, df in df_dict.items():
        labels = name.split("_")
        if len(labels) > 2:
            label = labels[-2]
        print("file = {}, label = {}".format(name, label))



    save_dataframes_to_excel(df_dict, path+"/{}_results.xlsx".format(label))

if __name__ == "__main__":
    main()