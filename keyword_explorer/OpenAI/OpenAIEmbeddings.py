import json
import time

import numpy as np
import openai
import openai.embeddings_utils as oaiu
import pandas as pd
import re
import ast
import pickle
from pypdf import PdfReader

from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms
from keyword_explorer.utils.MySqlInterface import MySqlInterface

from typing import List, Dict, Pattern, TextIO, Any

class OpenAIEmbeddings:
    #DEFAULT_TEXT_MODEL = "gpt-3.5-turbo-0301"
    DEFAULT_TEXT_MODEL = "text-davinci-003"
    #DEFAULT_SUMMARY_MODEL = "gpt-3.5-turbo-0301"
    DEFAULT_SUMMARY_MODEL = "text-davinci-003"
    DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"
    oac:OpenAIComms
    msi:MySqlInterface


    def __init__(self, user="root", db="gpt_summary"):
        print("OpenAIEmbeddings")
        self.oac = OpenAIComms()
        self.msi = MySqlInterface(user, db)

    def create_question(self, question:str, context:str) -> str:
        #prompt=f"Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:"
        prompt=f"Answer the question based on the context below.\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:"
        return prompt

    def create_summary(self, context:str, word_len = 100) -> str:
        full_prompt="Summarize the following in approximately {} words: {}\n\n---\n\nSummary (approximately {} words):".format(word_len, context, word_len)
        return full_prompt

    def create_narrative(self, prompt:str, context:str) -> str:
        full_prompt=f"Using the following context, write a short story, based on the prompt.\n\nContext: {context}\n\n---\n\nStory: {prompt}"
        return full_prompt

    def create_list(self, prompt:str, context:str) -> str:
        full_prompt=f"Using the following context, {prompt}, based on the prompt.\n\nContext: {context}\n\n---\n\n{prompt}\n1)"
        return full_prompt

    def create_sequence(self, prompt:str, context:str) -> str:
        full_prompt=f"Using the following context, {prompt}, based on the prompt.\n\nContext: {context}\n\n---\n\n{prompt}\n1)"
        return full_prompt

    def get_response(self, prompt, model=DEFAULT_TEXT_MODEL, max_tokens=256):
        try:
            result = self.oac.get_prompt_result_params(prompt, max_tokens=max_tokens, temperature=0, top_p=1, frequency_penalty=0, presence_penalty=0, engine=model)
            return result
        except openai.error.RateLimitError as e:
            return e.user_message


    def answer_question(self, question:str, context:str, model=DEFAULT_TEXT_MODEL, max_len=1800,
            size="ada", debug=False, max_tokens=150, stop_sequence=None) -> str:
        """
        Answer a question based on the most similar context from the dataframe texts
        """
        prompt = self.create_question(question, context)
        return self.get_response(prompt, model, max_tokens)

    def get_origins_text(self, origins_list:List) -> List:
        origins_text = ", ".join(map(str, origins_list))
        # sql = "select id, parsed_text from gpt_summary.table_parsed_text where id in ({})".format(origins_text)
        sql = "select id, text_name, parsed_text from gpt_summary.parsed_text_view where id in ({})".format(origins_text)
        # print("sql = {}".format(sql))
        response = self.msi.read_data(sql)
        d:Dict
        to_return = []
        for d in response:
            to_return.append("{} {}: {}".format(d['text_name'], d['id'], d['parsed_text']))
        return to_return

    def parse_content(self, raw_text:str, r_str:str = r"([\.!?()]+)", default_print:int = 0, min_chars:int = 10) -> List:
        # print("OpenAIEmbeddings:parse_content r_str = {}".format(r_str))
        cr_regex = re.compile("\n+")
        reg = re.compile(r_str)
        l = cr_regex.split(raw_text)
        s1:str
        s2:str
        s_list = []
        i = 0
        while i < len(l):
            s = reg.sub(" ", l[i])
            s1 = s.strip()
            while i < len(l)-1:
                s2 = l[i+1]
                if len(s2) < min_chars:
                    s1 += s2
                    i += 1
                else:
                    break
            s_list.append(s1)
            i += 1

        for i in range(default_print):
            print("OpenAIEmbeddings:parse_file_str{}".format(s_list[i]))

        return s_list

    def parse_text_file(self, filename:str, r_str:str = r"([\.!?()]+)", default_print:int = 0, min_chars = 10) -> List:
        f = open(filename, mode="r", encoding="utf-8", errors='replace')

        s = f.read()
        f.close()
        s_list = self.parse_content(s, r_str, default_print, min_chars)

        return s_list

    def parse_pdf_file(self, filename:str, r_str:str = r"([\.!?()]+)", default_print:int = 0, min_chars = 10) -> List:
        reader = PdfReader(filename)
        number_of_pages = len(reader.pages)
        full_list = []
        print("\tnumber of pages = {}".format(number_of_pages))
        for i in range(number_of_pages):
            print("\tParsing page {} of {}".format(i, number_of_pages))
            page = reader.pages[i]
            text = page.extract_text()
            s_list = self.parse_content(text, r_str=r_str)
            full_list.extend(s_list)
        return full_list

    def get_embeddings(self, text_list:List, submit_size:int = 10, max:int = -1) -> pd.DataFrame:
        d_list = []
        ed:Dict
        md:Dict
        num_text = len(text_list)
        # for i in range(0, num_text+submit_size-1, submit_size):
        #    s_list = text_list[i:min(num_text, i+submit_size])
        for i in range(0, num_text, submit_size):
            s_list = text_list[i:i+submit_size]
            percent_done = float(i/num_text) * 100

            embd_list = self.oac.get_embedding_list(s_list, self.DEFAULT_EMBEDDING_MODEL)
            mod_list = self.oac.get_moderation_vals(s_list)
            for i in range(len(s_list)):
                ed = embd_list[i]
                md = mod_list[i]
                text = s_list[i]
                embedding = np.array(ed['embedding'])
                jmod = json.dumps(md['category_scores'])
                d = {"text":text, "embedding":embedding, "moderation":jmod}
                d_list.append(d)
            print("{:2f}%: {}".format(percent_done, s_list[0]))
            if max > 0 and i > max:
                break

        df = pd.DataFrame(d_list)
        return df

    def set_summary_embeddings(self, text_name:str, group_name:str, limit:int = -1, database="gpt_summary", user="root") -> int:
        d:Dict

        # Make sure there is a project to use
        sql = "select * from table_source where text_name = %s and group_name = %s"
        vals = (text_name, group_name)
        results = self.msi.read_data(sql, vals)
        if len(results) == 0:
            print("Unable to find project '{}':'{}'".format(text_name, group_name))
            return -1
        d = results[0]
        project_id = d['id']
        # take some set of lines from the parsed text table and produce summary lines in the summary text table

        sql = 'select id, source, summary_text from table_summary_text where source = %s and embedding is NULL'
        if limit != -1:
            sql = '{} LIMIT {}'.format(sql, limit)
        vals = (project_id, )

        results = self.msi.read_data(sql, vals)
        text_list = []
        id_list = []
        for d in results:
            text_list.append(d['summary_text'])
            id_list.append(d['id'])

        print("OpenAIEmbeddings.set_summary_embeddings() setting up DataFrame")
        df = self.get_embeddings(text_list)
        df['id'] = id_list
        emb:np.array
        print("OpenAIEmbeddings.set_summary_embeddings() writing to DB")
        for index, row in df.iterrows():
            id = row['id']
            emb = row['embedding']
            moderation = row['moderation']
            # print("[{}], {}".format(id, emb))
            sql = "update table_summary_text set embedding = %s, moderation = %s where id = %s"
            vals = (emb.dumps(), moderation, id)
            self.msi.write_sql_values_get_row(sql, vals)

        print("OpenAIEmbeddings.set_summary_embeddings() Processed {} embeddings".format(len(df.index)))

    def create_context(self, question:str, df:pd.DataFrame, max_len=400, size="ada") -> [str, List]:
        """
        Create a context for a question by finding the most similar context from the dataframe
        """
        # print("Text: [{}]".format(question))
        # Get the embeddings for the question
        # return openai.Embedding.create(input = [text], model=engine)['data'][0]['embedding']
        #q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']
        q_embeddings = self.oac.get_embedding(question)

        # Get the distances from the embeddings
        df['distances'] = oaiu.distances_from_embeddings(q_embeddings, list(df['embedding'].values), distance_metric='cosine')


        returns = []
        origins = []
        cur_len = 0
        df2 = df.sort_values('distances', ascending=True)
        # Sort by distance and add the text to the context until the context is too long
        for i, row in df2.iterrows():
            text = str(row['origins'])
            # print("OpenAIEmbeddings.create_context = {}".format(text))
            origin = ast.literal_eval(text)
            origins += origin
            # Add the length of the text to the current length
            text = str(row['parsed_text'])
            words = text.split()
            cur_len += len(words)

            # If the context is too long, break
            if cur_len > max_len:
                break

            # Else add it to the text that is being returned
            # print("row [{}] distance = {} text = [{}]".format(row['row_id'], row['distances'], text))
            # reverse the order of the context
            returns.append(text)

        # Return the context so the best match is closest to the question
        #return "\n\n###\n\n".join(reversed(returns))
        return ("\n\n###\n\n".join(returns), origins)

    def build_text_to_summarize(self, results:List, row_count:int, words_to_summarize = 200, overlap = 2, word_len = 100) -> Dict:
        num_lines = len(results)
        d:Dict
        context:str = ""
        query = "Provide a summary of the following:\n"
        row_list = []
        origin_list = []
        word_count = 0
        # we want to overlap our summaries a bit for better coverage
        if row_count > overlap:
            row_count -= overlap
        while word_count < words_to_summarize and row_count < num_lines:
            #print("count = {}".format(count))
            d = results[row_count]
            text = d['parsed_text']
            word_count += context.count(" ")
            row_list.append(d['text_id'])
            if 'origins' in d: # this would be from a summary
                l = ast.literal_eval(d['origins'])
                origin_list += l
            else: # this is working on the original text
                origin_list.append(d['text_id'])

            # query = "{} [{}] {}".format(query, d['text_id'], text)
            context = "{} {}.".format(context, text)
            row_count += 1

        query = self.create_summary(context, word_len)
        d = {'query':query, 'count':row_count, 'row_list':row_list, 'origins':origin_list}
        return d

    def summarize_raw_text(self, text_name:str, group_name:str, max_lines = -1, words_to_summarize = 200, engine=DEFAULT_TEXT_MODEL, max_tokens = 256) -> int:
        # take some set of lines from the parsed text table and produce summary lines in the summary text table
        print("OpenAIEmbeddings.summarize_raw_text(): saving to '{}':'{}'".format(text_name, group_name))
        d:Dict
        sql = "select * from table_source where text_name = %s and group_name = %s"
        vals = (text_name, group_name)
        results = self.msi.read_data(sql, vals)
        if len(results) == 0:
            print("Unable to find project '{}':'{}'".format(text_name, group_name))
            return -1
        d = results[0]
        project_id = d['id']
        # then take those summaries and recursively summarize until the target line count is reached
        sql = "select text_id, parsed_text from source_text_view where source_id = %s and summary_id = -1"
        if max_lines != -1:
            sql = "{} limit {}".format(sql, max_lines)
        vals = (project_id,)
        results = self.msi.read_data(sql, vals)

        num_lines = len(results)
        count = 0
        level = 1
        summary_count = 0
        old_summary = "unset"
        while count < num_lines:
            d = self.build_text_to_summarize(results, count, words_to_summarize)
            # run the query and store the result. Update the parsed text table with the summary id
            summary = self.oac.get_prompt_result_params(d['query'], engine=engine, temperature=0, presence_penalty=0.8, frequency_penalty=0, max_tokens=max_tokens)
            if summary == old_summary:
                print("OpenAIEmbeddings.summarize_raw_text() Same summary error, returning early!")
                print("\t{}".format(d))
                return summary_count
            old_summary = summary

            sql = "insert into table_summary_text (source, level, summary_text, origins) values (%s, %s, %s, %s)"
            vals = (project_id, level, summary, str(d['origins']))
            row_id = self.msi.write_sql_values_get_row(sql, vals)
            summary_count += 1
            if num_lines > 0:
                print("[{}] ({} of {} = {:.2f}%) {}".format(row_id, count, num_lines, float(count/num_lines)*100, summary))

            for r in d['row_list']:
                sql = "update table_parsed_text set summary_id = %s where id = %s"
                vals = (row_id, r)
                self.msi.write_sql_values_get_row(sql, vals)

            if d['count'] > count:
                count = d['count']
            else:
                print("OpenAIEmbeddings.summarize_raw_text() manually incrementing count from {} to {}".format(count, count + 1))
                count += 1

        return summary_count

    def summarize_summary_text(self, text_name:str, group_name:str, source_level:int, max_lines = -1, words_to_summarize = 200, database="gpt_summary", user="root") -> int:
        # take some set of lines from the parsed text table and produce summary lines in the summary text table
        d:Dict

        # Make sure there is a project to use
        sql = "select * from table_source where text_name = %s and group_name = %s"
        vals = (text_name, group_name)
        results = self.msi.read_data(sql, vals)
        if len(results) == 0:
            print("Unable to find project '{}':'{}'".format(text_name, group_name))
            return -1
        d = results[0]
        project_id = d['id']

        # get all the items that are left to summarice in this level
        target_level = source_level +1
        # get all the lines in the source that have not been summarized yet
        sql = "select text_id, parsed_text, origins from summary_text_view where proj_id = %s and level = %s and summary_id = -1"
        vals = (project_id, source_level)
        results = self.msi.read_data(sql, vals)
        num_lines = len(results)
        print("----------- lines to summarize = {} rows, source_level = {} -----------------".format(num_lines, source_level))

        # build the summary
        count = 0
        while count < num_lines:
            d = self.build_text_to_summarize(results, count, words_to_summarize)
            # run the query and store the result. Update the parsed text table with the summary id
            summary = self.oac.get_prompt_result_params(d['query'], engine=self.DEFAULT_SUMMARY_MODEL, temperature=0, presence_penalty=0.8, frequency_penalty=0, max_tokens=128)
            sql = "insert into table_summary_text (source, level, summary_text, origins) values (%s, %s, %s, %s)"
            vals = (project_id, target_level, summary, str(d['origins']))
            row_id = self.msi.write_sql_values_get_row(sql, vals)
            print("[{}] - {} - {}".format(row_id, d['row_list'], summary))

            for r in d['row_list']:
                sql = "update table_summary_text set summary_id = %s where id = %s"
                vals = (row_id, r)
                self.msi.write_sql_values_get_row(sql, vals)
            count = d['count']

        # Figure out how many lines are in the new summary
        sql = "select count(*) from summary_text_view where proj_id = %s and level = %s"
        vals = (project_id, target_level)
        results = self.msi.read_data(sql, vals)
        num_lines = results[0]['count(*)']

        return num_lines


    def store_project_data(self, text_name:str, group_name_str, df:pd.DataFrame, database="gpt_summary", user="root") -> int:
        sql = "select * from table_source where text_name = %s and group_name = %s"
        vals = (text_name, group_name_str)
        results = self.msi.read_data(sql, vals)
        if len(results) == 0:
            print("No db entry for '{}' '{}': creating entry".format(text_name, group_name_str))
            sql = "insert into table_source (text_name, group_name) values (%s, %s)"
            source_id = self.msi.write_sql_values_get_row(sql, vals)
        else:
            source_id = results[0]['id']

        print("source_id = {}".format(source_id))
        for index, row in df.iterrows():
            text = row['text']
            embedding = np.array(row['embedding'])
            moderation = row['moderation']
            sql = "insert into gpt_summary.table_parsed_text (source, parsed_text, embedding, moderation) values (%s, %s, %s, %s)"
            vals = (source_id, text, embedding.dumps(), moderation)
            self.msi.write_sql_values_get_row(sql, vals)

    def load_project_parsed_text(self, text_name:str, group_name:str, database="gpt_summary", user="root", limit = -1) -> pd.DataFrame:
        sql = "select * from table_source where text_name = %s and group_name = %s"
        vals = (text_name, group_name)
        results = self.msi.read_data(sql, vals)
        if len(results) == 0:
            print("No db entry for '{}' '{}'")
            return pd.DataFrame() # Return an empty DataFrame
        else:
            source_id = results[0]['id']

        print("OpenAIEmbeddings.load_project_parsed_text(): pulling text for '{}'".format(text_name))
        sql = "select id as row_id, parsed_text, embedding from gpt_summary.table_parsed_text where source = {}".format(source_id)
        if limit > 0:
            sql += " limit {}".format(limit)

        results = self.msi.read_data(sql)

        print("\tProcessing {} lines".format(len(results)))
        d:Dict
        for d in results:
            emb = d['embedding']
            d['embedding'] = pickle.loads(emb)
            # print(d)

        df = pd.DataFrame(results)
        print("\tDone")
        return df

    def results_to_df(self, results:List) -> pd.DataFrame:
        print("\tProcessing {} lines".format(len(results)))
        d:Dict
        for d in results:
            emb = d['embedding']
            d['embedding'] = pickle.loads(emb)
            if 'origins' in d:
                orig = d['origins']
                d['origins'] = ast.literal_eval(orig)
            else:
                d['origins'] = [d['text_id']]
            # print(d)

        df = pd.DataFrame(results)
        return df

    def load_project_summary_text(self, text_name:str, group_name:str, level = 1, limit = -1) -> pd.DataFrame:
        sql = "select * from table_source where text_name = %s and group_name = %s"
        vals = (text_name, group_name)
        results = self.msi.read_data(sql, vals)
        if len(results) == 0:
            print("No db entry for '{}' '{}': creating entry")
            return pd.DataFrame() # Return an empty DataFrame
        else:
            source_id = results[0]['id']

        print("OpenAIEmbeddings.load_project_summary_text(): pulling text for '{}'".format(text_name))
        sql = "select id as row_id, summary_text as parsed_text, embedding, origins from gpt_summary.table_summary_text where source = %s and level = %s"
        vals = (source_id, level)
        if limit > 0:
            sql += " limit {}".format(limit)

        results = self.msi.read_data(sql, vals)

        return self.results_to_df(results)

    def get_source_text(self, row_id_list:List) -> List:
        s = ", ".join(map(str,row_id_list))
        sql = "select id, parsed_text from gpt_summary.table_parsed_text where id in ({})".format(s)
        results = self.msi.read_data(sql)
        d:Dict
        to_return = []
        for d in results:
            to_return.append("line {}: {}".format(d['id'], d['parsed_text']))

        return to_return

    def close_db(self):
        self.msi.close()

    def tk_filter_string(self, input_string:str) -> str:
        """
        Filters the input string to remove characters outside the allowed range for Tkinter (U+0000 to U+FFFF).

        Args:
        input_string (str): The input string containing the characters to be filtered.

        Returns:
        str: A new string with disallowed characters removed.
        """
        allowed_range = range(0x0000, 0xFFFF + 1)
        filtered_string = ''.join([c for c in input_string if ord(c) in allowed_range])
        return filtered_string


def store_embeddings_main(text_name:str, group_name:str, file_str:str):
    oae = OpenAIEmbeddings()
    s_list = oae.parse_text_file(file_str, 10, default_print=10) # can be obtained here: https://www.gutenberg.org/files/2701/2701-h/2701-h.htm
    df = oae.get_embeddings(s_list[:100])
    #df = oae.get_embeddings(s_list)
    print(df)
    #oae.store_project_data("moby-dick", "melville", df)

def load_data_main():
    oae = OpenAIEmbeddings()
    df = oae.load_project_parsed_text("moby-dick", "melville", limit=1000)
    question = "what are best ways to hunt whales"
    cs = oae.create_context(question, df)
    print("Context string:\n{}".format(cs))

def summarize_project_main(min_rows = 10):
    oae = OpenAIEmbeddings()
    num_rows = oae.summarize_raw_text("on-war", "warfare")
    # while num_rows > min_rows:
    #   num_rows = oae.summarize_summary_text("moby-dick", "melville", source_level=4)
    #   print("summarize_project_main() num_rows = {}".format(num_rows))
    oae.set_summary_embeddings("on-war", "warfare")

def ask_question_main():
    oae = OpenAIEmbeddings()
    df = oae.load_project_summary_text("moby-dick", "melville")
    question = "Why is Ahab obsessed with Moby-Dick? Provide details."
    print("creating context")
    cs, origins_list = oae.create_context(question, df)
    # print("Context string:\n{}".format(cs))
    origins = oae.get_origins_text(origins_list)
    print("Origins:\n{}".format("\n".join(origins)))
    print("submitting question")
    answer = oae.answer_question(question=question, context=cs, model="gpt-3.5-turbo")
    print("\nAnswer:\n{}".format(answer))

    top_texts = 5
    print("Supporting top {} text:".format(top_texts))
    count = 0
    for index, row in df.sort_values('distances', ascending=True).iterrows():
        print("\tDist = {:.3f} Summary: {}".format(row['distances'], row['parsed_text']))
        source_list = oae.get_source_text(row['origins'])
        for s in source_list:
            print("\t\t{}".format(s))
        if count > top_texts:
            break
        count += 1

def fix_summary_origins():
    d:Dict
    d2:Dict
    msi = MySqlInterface("root", "gpt_summary", enable_writes = True)
    sql = "select distinct summary_id from table_summary_text"
    results = msi.read_data(sql)

    for d in results:
        summary_id = d['summary_id']
        sql = "select id, origins from table_summary_text where summary_id = %s and summary_id > 0"
        vals = (summary_id,)
        full_list = []
        results2 = msi.read_data(sql, vals)
        for d2 in results2:
            l = ast.literal_eval(d2['origins'])
            full_list += l
            # print("\t[{}]: {}".format(d2['id'],l))
        print("[{}]: {}".format(summary_id, full_list))
        sql = "update table_summary_text set origins = %s where id = %s"
        vals = (str(full_list), summary_id)
        msi.write_sql_values_get_row(sql, vals)

    msi.close()

if __name__ == "__main__":
    start_time = time.time()
    #store_embeddings_main(file_str="../../corpora/old-testament.txt", text_name="old-testament", group_name="bibles")
    # load_data_main()
    # ask_question_main()
    summarize_project_main()
    # fix_summary_origins()
    print("execution took {:.3f} seconds".format(time.time() - start_time))