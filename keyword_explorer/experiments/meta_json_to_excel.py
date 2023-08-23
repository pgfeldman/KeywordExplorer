import pandas as pd
import json
import os
import re
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

def save_sources_to_excel(dataframes:Dict, output_file:str):
    # Create a Pandas Excel writer using XlsxWriter as the engine
    engine_list = ["gpt-3.5-turbo-0301",
                   "gpt-3.5-turbo",
                   "gpt-4-0314",
                   "gpt-4"]

    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

    for sheet_name, df in dataframes.items():
        dict_list = []
        if sheet_name != 'Summary':
            labels = sheet_name.split("_")
            sheet_name = labels[-1]
            sheet_name = sheet_name.replace(".json", "")
            row_index = 2
            for index, row in df.iterrows():
                no_ctx_sources_value = row['no_ctx_sources']
                source_list = no_ctx_sources_value.split('\n')
                question_value = row['question']
                for s in source_list:
                    s = re.match(r'[^\w]*(.*)', s).group(1)
                    dict_list.append({"question": question_value, "source": s})
                    row_index += 1
            df = pd.DataFrame(dict_list)
            df.sort_values(by='source', key=lambda x: x.str.len(), ascending=False, inplace=True)
            # df_sorted = df.iloc[df['source'].str.len().argsort(reversed=True)]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    # Save the Excel file
    writer.save()

def save_dataframes_to_txt(dataframes:Dict, output_file:str):
    # Create a Pandas Excel writer using XlsxWriter as the engine
    engine_list = ["gpt-3.5-turbo-0301",
                   "gpt-3.5-turbo",
                   "gpt-4-0314",
                   "gpt-4"]


    df:pd.DataFrame
    row_dict:Dict
    with open(output_file, "w", encoding="utf-8") as f:
        for sheet_name, df in dataframes.items():
            labels = sheet_name.split("_")
            sheet_name = labels[-1]
            sheet_name = sheet_name.replace(".json", "")

            if sheet_name != 'Summary':
                f.write("\n=========================\nEngine: {}\n=========================\n".format(sheet_name))
                count = 0
                for row_dict in df.to_dict(orient='records'):
                    f.write("\n-------------------\n")
                    f.write("Question: \n{}\n".format(row_dict['question']))
                    f.write("\n-----------------\nContext response (No hallucinations?):\n{}\n".format(row_dict['context_response']))
                    f.write("\n-----------------\nNo context response (possible hallucinations) :\n{}\n".format(row_dict['no_context_response']))
                    count += 1
                    if count >= 2:
                        break


def save_dataframes_to_excel(dataframes:Dict, output_file:str):
    # Create a Pandas Excel writer using XlsxWriter as the engine
    engine_list = ["gpt-3.5-turbo-0301",
                   "gpt-3.5-turbo",
                   "gpt-4-0314",
                   "gpt-4"]

    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')


    # Loop through each dataframe and add it as a tab in the Excel file
    dataframe:pd.DataFrame
    for sheet_name, dataframe in dataframes.items():
        if sheet_name == 'Summary':
            # print("Summary = {}".format(dataframe))
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
            summary_sheet = writer.sheets[sheet_name]
            summary_sheet.write_string('A9','URL no context')
            summary_sheet.write_string('B9','no ctx good')
            summary_sheet.write_string('C9','no ctx bad')
            summary_sheet.write_string('D9','good/bad')
            row = 10
            for e in engine_list:
                summary_sheet.write_string('A{}'.format(row),e)
                summary_sheet.write_formula('B{}'.format(row), "=SUM('{}'!I$2:I$36)".format(e))
                summary_sheet.write_formula('C{}'.format(row), "=SUM('{}'!J$2:J$36)".format(e))
                summary_sheet.write_formula('D{}'.format(row), "=B{}/C{}".format(row, row))
                row += 1
            summary_sheet.write_string('A17','TOTAL')
            summary_sheet.write_formula('B17', "=SUM(B10:B16)")
            summary_sheet.write_formula('C17', "=SUM(C10:C16)")
            summary_sheet.write_formula('D17', "=B17/C17")

            summary_sheet.write_string('A19','URL context')
            summary_sheet.write_string('B19','ctx good')
            summary_sheet.write_string('C19','ctx bad')
            row = 20
            for e in engine_list:
                summary_sheet.write_string('A{}'.format(row),e)
                summary_sheet.write_formula('B{}'.format(row), "=SUM('{}'!G$2:G$36)".format(e))
                summary_sheet.write_formula('C{}'.format(row), "=SUM('{}'!H$2:H$36)".format(e))
                row += 1

            summary_sheet.write_string('A27','TOTAL')
            summary_sheet.write_formula('B27', "=SUM(B20:B26)")
            summary_sheet.write_formula('C27', "=SUM(C20:C26)")

            summary_sheet.write_string('A29','index tags')
            summary_sheet.write_string('B29','present')
            summary_sheet.write_string('C29','missing')
            summary_sheet.write_string('D29','mismatch')
            row = 30
            for e in engine_list:
                summary_sheet.write_string('A{}'.format(row),e)
                summary_sheet.write_formula('B{}'.format(row), "=COUNTIF('{}'!F2:F6, \"<>0\")".format(e))
                summary_sheet.write_formula('C{}'.format(row), "=COUNTIF('{}'!F2:F6, 0)".format(e))
                summary_sheet.write_formula('D{}'.format(row), "=COUNTIF('{}'!E7:E36, \"<>[]\")".format(e))
                row += 1

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



    #save_dataframes_to_excel(df_dict, path+"/{}_results.xlsx".format(label))
    #save_sources_to_excel(df_dict, path+"/{}_sources.xlsx".format(label))
    save_dataframes_to_txt(df_dict, path+"/{}_readable.txt".format(label))


if __name__ == "__main__":
    main()