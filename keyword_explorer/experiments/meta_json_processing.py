import pandas as pd
import json
import os
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
                experiments = json_data['experiments']
                df = pd.DataFrame(experiments)
                dataframes[filename] = df
    return dataframes

def save_dataframes_to_excel(dataframes, output_file):
    # Create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

    # Loop through each dataframe and add it as a tab in the Excel file
    for sheet_name, dataframe in dataframes.items():
        sheet_name = sheet_name.replace("meta_wrapping_", "")
        sheet_name = sheet_name.replace(".json", "")
        dataframe.to_excel(writer, sheet_name=sheet_name, index=False)

    # Save the Excel file
    writer.save()

def main():
    path = "../../data/meta_wrapping"
    df_dict = read_json_files_to_dataframe(path)

    name:str
    df:pd.DataFrame
    for name, df in df_dict.items():
        print(name)

    save_dataframes_to_excel(df_dict, path+"/results.xlsx")

if __name__ == "__main__":
    main()