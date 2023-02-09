import time

import numpy as np
import openai
import openai.embeddings_utils as oaiu
import pandas as pd
import re
import ast

from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms
from keyword_explorer.utils.MySqlInterface import MySqlInterface

from typing import List, Dict, Pattern

class OpenAIEmbeddings:
    oac:OpenAIComms


    def __init__(self):
        print("OpenAIEmbeddings")
        self.oac = OpenAIComms()

    def answer_question(self,
            df:pd.DataFrame,
            model="text-davinci-003",
            question="Am I allowed to publish model outputs to Twitter, without a human review?",
            max_len=1800,
            size="ada",
            debug=False,
            max_tokens=150,
            stop_sequence=None
    ):
        """
        Answer a question based on the most similar context from the dataframe texts
        """
        context = self.create_context(question, df, max_len=max_len, size=size)
        # If debug, print the raw model response
        if debug:
            print("Context:\n" + context)
            print("\n\n")

        try:
            # Create a completions using the question and context
            response = openai.Completion.create(
                prompt=f"Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:",
                temperature=0,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=stop_sequence,
                model=model,
            )
            return response["choices"][0]["text"].strip()
        except Exception as e:
            print(e)
            return ""

    def parse_text_file(self, filename:str, min_len:int = 5, r_str:str = r"\n+|[\.!?()“”]+", default_print:int = 0) -> List:
        s_list = []
        reg = re.compile(r_str)
        with open(filename, mode="r", encoding="utf-8") as f:
            s = f.read()
            s_list = reg.split(s)
            s_iter = filter(None, s_list)
            s_list = []
            for s in s_iter:
                if len(s) > min_len:
                    s_list.append(s.strip())

            for i in range(default_print):
                print("{}: {}".format(i, s_list[i]))

        return s_list

    def get_embeddings(self, text_list:List, max:int = -1) -> pd.DataFrame:
        d_list = []
        count = 0

        for s in text_list:
            percent_done = float(count/len(text_list)) * 100
            try:
                result = self.oac.get_embedding('hello, world', 'text-embedding-ada-002')
                d = {"text":s, "embedding":result}
                d_list.append(d)
                print("{:2f}%: {}".format(percent_done, s))
                if max > 0 and count > max:
                    break
                count += 1
                waitcount = 0
            except openai.error.APIError as e:
                waitcount += 1
                time_to_wait = 5 * waitcount
                print("OpenAIEmbeddings.get_embeddings error, returning early. Message = {}".format(e.user_message))
                if waitcount > 5:
                    df = pd.DataFrame(d_list)
                    return df
                print("waiting {} seconds".format(time_to_wait))
                time.sleep(time_to_wait)

        #return normally
        df = pd.DataFrame(d_list)
        return df

    def create_context(self, question:str, df:pd.DataFrame, max_len=300, size="ada"):
        """
        Create a context for a question by finding the most similar context from the dataframe
        """

        # Get the embeddings for the question
        q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']

        # Get the distances from the embeddings
        df['distances'] = oaiu.distances_from_embeddings(q_embeddings, list(df['embedding'].values), distance_metric='cosine')


        returns = []
        cur_len = 0

        # Sort by distance and add the text to the context until the context is too long
        for i, row in df.sort_values('distances', ascending=True).iterrows():

            # Add the length of the text to the current length
            text = str(row['parsed_text'])
            words = text.split()
            cur_len += len(words)

            # If the context is too long, break
            if cur_len > max_len:
                break

            # Else add it to the text that is being returned
            print("distance = {} text = {}, ".format(row['distances'], text))
            returns.append(text)

        # Return the context
        return "\n\n###\n\n".join(returns)

    def store_project_data(self, text_name:str, group_name_str, df:pd.DataFrame, database="gpt_summary", user="root"):
        msi = MySqlInterface(user, database)
        sql = "select * from table_source where text_name = %s and group_name = %s"
        vals = (text_name, group_name_str)
        results = msi.read_data(sql, vals)
        if len(results) == 0:
            print("No db entry for '{}' '{}': creating entry")
            sql = "insert into table_source (text_name, group_name) values (%s, %s)"
            source_id = msi.write_sql_values_get_row(sql, vals)
        else:
            source_id = results[0]['id']

        print("source_id = {}".format(source_id))
        for index, row in df.iterrows():
            text = row['text']
            embedding = row['embedding']
            sql = "insert into gpt_summary.table_parsed_text (source, parsed_text, embedding) values (%s, %s, %s)"
            vals = (source_id, text, embedding)
            msi.write_sql_values_get_row(sql, vals)

        msi.close()

    def load_project_data(self, text_name:str, group_name_str, database="gpt_summary", user="root", limit = -1) -> pd.DataFrame:
        msi = MySqlInterface(user, database, enable_writes = False)
        sql = "select * from table_source where text_name = %s and group_name = %s"
        vals = (text_name, group_name_str)
        results = msi.read_data(sql, vals)
        if len(results) == 0:
            print("No db entry for '{}' '{}': creating entry")
            return pd.DataFrame() # Return an empty DataFrame
        else:
            source_id = results[0]['id']

        print("OpenAIEmbeddings.load_project_data(): pulling text for '{}'".format(text_name))
        sql = "select * from gpt_summary.table_parsed_text where source = {}".format(source_id)
        if limit > 0:
            sql += " limit {}".format(limit)

        results = msi.read_data(sql)

        msi.close()

        print("\tProcessing {} lines".format(len(results)))
        d:Dict
        for d in results:
            emb = d['embedding']
            emb_l = ast.literal_eval(emb)
            d['embedding'] = np.array(emb_l)
            # print(d)

        df = pd.DataFrame(results)
        print("\tDone")
        return df


    def write_csv(self, filename:str, df:pd.DataFrame):
        df.to_csv(filename)

    def read_csv(self, filename:str) -> pd.DataFrame:
        print("OpenAIEmbeddings.read_csv(): reading {}".format(filename))
        df = pd.read_csv(filename, index_col=0)
        print("\tconverting")
        d = df.to_dict()
        de = d['embedding']
        for key, val in de.items():
            l = ast.literal_eval(val)
            de[key] = l
        df = pd.DataFrame(d)
        print("\tready")
        return df



def create_csv_main():
    oae = OpenAIEmbeddings()
    s_list = oae.parse_text_file("../../corpora/moby-dick-3.txt", 10, default_print=10) # can be obtained here: https://www.gutenberg.org/files/2701/2701-h/2701-h.htm
    df = oae.get_embeddings(s_list)
    print(df)
    df.to_csv("../../data/moby-dick-embeddings_3.csv")
    print("done writing file")

def store_embeddings_main():
    df = pd.DataFrame()
    oae = OpenAIEmbeddings()
    oae.store_project_data("moby-dick", "melville", df)

def load_data_main():
    oae = OpenAIEmbeddings()
    df = oae.load_project_data("moby-dick", "melville", limit=1000)
    cs = oae.create_context("There go the ships; there is that Leviathan whom thou hast made to play therein", df)
    print(cs)

if __name__ == "__main__":
    # create_csv_main()
    # store_embeddings_main()
    load_data_main()