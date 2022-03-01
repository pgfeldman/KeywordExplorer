from datetime import datetime
import openai
import os
from typing import List, Dict, Set, Pattern

class OpenAIComms:
    openai.api_key = os.environ.get("OPENAI_KEY")
    engines:List = ["davinci", "curie", "babbage", "ada", "text-davinci-001", "text-curie-001", "text-babbage-001", "text-ada-001"]
    engine:str = engines[0]
    max_tokens:int = 30 # The maximum number of tokens to generate. Requests can use up to 2048 tokens shared between prompt and completion. (One token is roughly 4 characters for normal English text)
    temperature:float = 0.4 # What sampling temperature to use. Higher values means the model will take more risks. Try 0.9 for more creative applications, and 0 (argmax sampling) for ones with a well-defined answer.
    top_p:float = 1 # An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
    logprobs:int = 1 # Include the log probabilities on the logprobs most likely tokens, as well the chosen tokens. For example, if logprobs is 10, the API will return a list of the 10 most likely tokens. the API will always return the logprob of the sampled token, so there may be up to logprobs+1 elements in the response.
    num_responses:int = 1 # How many completions to generate for each prompt.
    presence_penalty:float = 0.3 # Number between 0 and 1 that penalizes new tokens based on whether they appear in the text so far. Increases the model's likelihood to talk about new topics.
    frequency_penalty:float = 0.3 # Number between 0 and 1 that penalizes new tokens based on their existing frequency in the text so far. Decreases the model's likelihood to repeat the same line verbatim.


    def __init__(self, engine_id:int = 0):
        self.engine = self.engines[engine_id]

    #default to the cheap model to spend less money!
    def set_parameters(self, max_tokens:int = 30, temperature:float = 0.4, top_p:float = 1, logprobs:int = 1,
                       num_responses:int = 1, presence_penalty:float = 0.3, frequency_penalty:float = 0.3, engine_id:int=2):
        self.engine = self.engines[engine_id]
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.logprobs = logprobs
        self.num_responses = num_responses
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty


    def get_prompt_result(self, prompt:str, print_result:bool = False) -> List:
        response = openai.Completion.create(engine=self.engine, prompt=prompt, max_tokens=self.max_tokens,
                                            temperature=self.temperature, top_p=self.top_p, logprobs=self.logprobs,
                                            presence_penalty=self.presence_penalty, frequency_penalty=self.frequency_penalty,
                                            n=self.num_responses)
        if print_result:
            print(response)
        to_return = []
        choices = response['choices']
        for c in choices:
            to_return.append(c['text'])

        return to_return

    def get_embedding(self, text:str, engine="davinci-similarity"):
        # from https://beta.openai.com/docs/guides/embeddings/what-are-embeddings
        # replace newlines, which can negatively affect performance.
        text = text.replace("\n", " ")
        return openai.Engine(id=engine).embeddings(input = [text])['data'][0]['embedding']

    def set_engine(self, id:int = -1, name:str = None):
        if id != -1:
            self.engine = self.engines[id]
        elif name != None and name in self.engines:
            self.engine = name

    def get_engine(self) -> str:
        return self.engine

    def list_engines(self):
        result = openai.Engine.list()
        print(result)

    def key_exists(self) -> bool:
        val = os.environ.get("OPENAI_KEY")
        if val == None:
            return False
        return True


def main():
    oai = OpenAIComms()
    # oai.list_engines()
    # result = oai.get_embedding('hello, world', 'text-similarity-ada-001')
    # print(result)
    for name in oai.engines:
        oai.set_engine(name=name)
        print("engine = {}".format(oai.get_engine()))
        result = oai.get_prompt_result("one, two, three", print_result=False)
        print(result)

if __name__ == '__main__':
    main()