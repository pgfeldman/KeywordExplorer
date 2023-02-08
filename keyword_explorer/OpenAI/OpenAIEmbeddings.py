import numpy as np
import openai
import openai.embeddings_utils as oaiu
import pandas as pd
import re

from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms

class OpenAIEmbeddings:
    oac:OpenAIComms

    def __init__(self):
        print("OpenAIEmbeddings")
        self.oac = OpenAIComms()

    def create_context(self, question:str, df:pd.DataFrame, max_len=1800, size="ada") -> str:
        """
        Create a context for a question by finding the most similar context from the dataframe
        """

        # Get the embeddings for the question
        q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']

        # Get the distances from the embeddings
        embeddings_list= list(df['embeddings'].values)
        df['distances'] = oaiu.distances_from_embeddings(q_embeddings, embeddings_list, distance_metric='cosine')


        returns = []
        cur_len = 0

        # Sort by distance and add the text to the context until the context is too long
        for i, row in df.sort_values('distances', ascending=True).iterrows():

            # Add the length of the text to the current length
            cur_len += row['n_tokens'] + 4

            # If the context is too long, break
            if cur_len > max_len:
                break

            # Else add it to the text that is being returned
            returns.append(row["text"])

        # Return the context
        return "\n\n###\n\n".join(returns)

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

    def parse_text_file(self, filename:str, min_len:int = 5, r_str:str = r"\n+|[\.!?()“”]+") -> bool: # |([\.!?]\")") -> bool:

        reg = re.compile(r_str)
        with open(filename, mode="r", encoding="utf-8") as f:
            s = f.read()
            s_list = reg.split(s)
            s_iter = filter(None, s_list)
            s_list = []
            for s in s_iter:
                if len(s) > min_len:
                    s_list.append(s.strip())

            for i in range(25):
                print("{}: {}".format(i, s_list[i]))

            return True

        return False

def main():
    oae = OpenAIEmbeddings()
    oae.parse_text_file("../../corpora/moby-dick.txt", 10) # can be obtained here: https://www.gutenberg.org/files/2701/2701-h/2701-h.htm

if __name__ == "__main__":
    main()