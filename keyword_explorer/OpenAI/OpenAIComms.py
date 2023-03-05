from datetime import datetime
import numpy as np
import openai
import os
import time
from enum import Enum
from typing import List, Dict, Set, Pattern

class CHAT_ROLES(Enum):
    USER = "user"
    SYSTEM = "system"
    ASSIST = "assistant"
class ChatUnit:
    roles:CHAT_ROLES
    role:str
    content:str

    def __init__(self, content:str, role:CHAT_ROLES=CHAT_ROLES.USER):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict:
        return {"role":self.role.value, "content": self.content}

class OpenAIComms:
    openai.api_key = os.environ.get("OPENAI_KEY")
    engines:List = ["text-davinci-003", "davinci", "curie", "babbage", "ada", "text-curie-001", "text-babbage-001", "text-ada-001"]
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

    # more options (temperature, etc) are here: https://platform.openai.com/docs/api-reference/chat/create
    def get_chat_complete(self, unit_list:List, engine:str = "gpt-3.5-turbo", max_tokens:int = 128, temperature:float = 0.4, top_p:float = 1,
                          presence_penalty:float = 0.3, frequency_penalty:float = 0.3) -> str:
        cu:ChatUnit
        goodread = False
        waitcount = 0
        waitmax = 0
        s:str
        time_to_wait = 5
        while not goodread:
            try:
                response = openai.ChatCompletion.create(
                    model=engine,
                    max_tokens = max_tokens,
                    temperature = temperature,
                    top_p = top_p,
                    presence_penalty = presence_penalty,
                    frequency_penalty = frequency_penalty,
                    messages=[cu.to_dict() for cu in unit_list]
                )
                d = response['choices'][0]
                s = d['message']['content']
                return s.strip()
            except openai.error.APIConnectionError as e:
                print("OpenAIComms.get_prompt_result(): {}".format(e.user_message))
                return "Error reaching OpenAI completion endpoint"

            except openai.error.RateLimitError:
                print("OpenAIComms.get_prompt_result_params() waiting {} seconds".format(time_to_wait))
                time.sleep(time_to_wait)
                waitcount += 1
                if waitcount < waitmax:
                    return "{} is currently overloaded with other requests".format(engine)

    def get_prompt_result_params(self, prompt:str, engine:str = "text-davinci-003", max_tokens:int = 30, temperature:float = 0.4, top_p:float = 1, logprobs:int = 1,
                                 num_responses:int = 1, presence_penalty:float = 0.3, frequency_penalty:float = 0.3) -> str:
        if "gpt-3.5" in engine:
            print("OpenAICommsget_prompt_result_params(): Using Chat interface")
            l = [ChatUnit(prompt, CHAT_ROLES.USER)]
            return self.get_chat_complete(l, max_tokens=max_tokens, temperature=temperature, top_p=top_p,
                                          presence_penalty=presence_penalty, frequency_penalty=frequency_penalty)

        goodread = False
        waitcount = 0
        waitmax = 0
        time_to_wait = 5
        while not goodread:
            try:
                response = openai.Completion.create(engine=engine, prompt=prompt, max_tokens=max_tokens,
                                                    temperature=temperature, top_p=top_p, logprobs=logprobs,
                                                    presence_penalty=presence_penalty, frequency_penalty=frequency_penalty,
                                                    n=num_responses)
                choices = response['choices']
                s = choices[0]['text']
                goodread = True
                return s.strip()
            except openai.error.APIConnectionError as e:
                print("OpenAIComms.get_prompt_result(): {}".format(e.user_message))
                return "Error reaching OpenAI completion endpoint"

            except openai.error.RateLimitError:
                print("OpenAIComms.get_prompt_result_params() waiting {} seconds".format(time_to_wait))
                time.sleep(time_to_wait)
                waitcount += 1
                if waitcount < waitmax:
                    return "{} is currently overloaded with other requests".format(engine)


    def get_prompt_result(self, prompt:str, print_result:bool = False) -> List:
        to_return = []
        goodread = False
        waitcount = 0
        waitmax = 10
        time_to_wait = 5
        while not goodread:
            goodread = False
            try:
                response = openai.Completion.create(engine=self.engine, prompt=prompt, max_tokens=self.max_tokens,
                                                    temperature=self.temperature, top_p=self.top_p, logprobs=self.logprobs,
                                                    presence_penalty=self.presence_penalty, frequency_penalty=self.frequency_penalty,
                                                    n=self.num_responses)
                if print_result:
                    print(response)
                choices = response['choices']
                for c in choices:
                    to_return.append(c['text'])
                goodread = True
                waitcount = 0

            except openai.error.APIConnectionError as e:
                print("OpenAIComms.get_prompt_result(): {}".format(e.user_message))
                to_return.append("Error reaching OpenAI completion endpoint")
                goodread = True

            except openai.error.RateLimitError:
                print("OpenAIComms.get_prompt_result_params() waiting {} seconds".format(time_to_wait))
                time.sleep(time_to_wait)
                waitcount += 1
                if waitcount < waitmax:
                    to_return.append( "{} is currently overloaded with other requests".format(self.engine))
                    goodread = True

        return to_return

    def get_embedding(self, text:str, engine="text-embedding-ada-002"):
        # from https://beta.openai.com/docs/guides/embeddings/what-are-embeddings
        # replace newlines, which can negatively affect performance.
        text = text.replace("\n", " ")
        #return openai.Engine(id=engine).embeddings(input = [text])['data'][0]['embedding']
        return openai.Embedding.create(input = text, model=engine)['data'][0]['embedding']

    def get_embedding_list(self, text_list:List, engine="text-embedding-ada-002") -> List:
        # from https://beta.openai.com/docs/guides/embeddings/what-are-embeddings
        good_read = False
        waitcount = 0
        while not good_read:
            try:
                results =  openai.Embedding.create(input = text_list, model=engine)
                d_list = []
                data_list = results['data']
                d:Dict
                i = 0
                for d in data_list:
                    a = np.array(d["embedding"])
                    d_list.append({"text":text_list[i], "embedding":a})
                    i += 1
                return d_list

            except openai.error.APIError as e:
                waitcount += 1
                time_to_wait = 5 * waitcount
                print("OpenAIComms.get_embedding_list error, returning early. Message = {}".format(e.user_message))
                if waitcount > 5:
                    print("OpenAIComms.get_embedding_list error, returning early.")
                    return [{"text":"unset", "embedding":np.array([0, 0, 0])}]
                print("OpenAIComms.get_embedding_list waiting {} seconds".format(time_to_wait))
                time.sleep(time_to_wait)

    def set_engine(self, id:int = -1, name:str = None):
        if id != -1:
            self.engine = self.engines[id]
        elif name != None and name in self.engines:
            self.engine = name

    def get_engine(self) -> str:
        return self.engine

    def list_models(self, keep_list:List = [""], exclude_list:List = []) -> List:
        result:openai.OpenAIObject = openai.Model.list()
        dl = result.data
        name_set = set()
        for d in dl:
            s = d['id']
            exclude = False
            for e in exclude_list:
                if e in s:
                    exclude = True
                    break
            if not exclude:
                for k in keep_list:
                    if k in s:
                        name_set.add(s)
        return list(name_set)

    def key_exists(self) -> bool:
        val = os.environ.get("OPENAI_KEY")
        if val == None:
            return False
        return True


def embedding_main():
    oai = OpenAIComms()

    print("\navailable embedding models:")
    lm = oai.list_models(keep_list = ["embed", "similarity"])
    for m in sorted(lm):
        print(m)

    print("\navailable text models:")
    lm = oai.list_models(exclude_list = ["embed", "similarity", "code", "edit", "search", "audio", "instruct", "2020", "if", "insert"])
    for m in sorted(lm):
        print(m)


    print("\nembedding:")
    result = oai.get_embedding('hello, world', 'text-embedding-ada-002')
    #s = ",".join(str(e) for e in result)
    s = ",".join(map(str, result))
    print(s)

    print("\nembedding list:")
    text_list = ["Supplied by a Late Consumptive Usher to a Grammar School",
                 "The pale Usher—threadbare in coat, heart, body, and brain; I see him now",
                 "He was ever dusting his old lexicons and grammars, with a queer handkerchief, mockingly embellished with all the gay flags of all the known nations of the world",
                 "He loved to dust his old grammars; it somehow mildly reminded him of his mortality",
                "While you take in hand to school others, and to teach them by what name a whale-fish is to be called in our tongue, leaving out, through ignorance, the letter H, which almost alone maketh up the signification of the word, you deliver that which is not true",
                "This animal is named from roundness or rolling; for in Dan",
                "hvalt is arched or vaulted",
                "—Webster’s Dictionary",
                "* * * It is more immediately from the Dut",
                "Walw-ian, to roll, to wallow"
    ]
    result = oai.get_embedding_list(text_list, 'text-embedding-ada-002')
    d:Dict
    for d in result:
        print(d)

    print("\ngeneration")
    for name in oai.engines:
        oai.set_engine(name=name)
        print("engine = {}".format(oai.get_engine()))
        result = oai.get_prompt_result("one, two, three", print_result=False)
        print(result)

def chat_main():
    oai = OpenAIComms()


    print("\navailable text models:")
    lm = oai.list_models(exclude_list = ["embed", "similarity", "code", "edit", "search", "audio", "instruct", "2020", "if", "insert"])
    for m in sorted(lm):
        print(m)

    l = []
    l.append(ChatUnit("You are a helpful assistant.", CHAT_ROLES.SYSTEM))
    l.append(ChatUnit("Who won the world series in 2020?", CHAT_ROLES.USER))
    l.append(ChatUnit("The Los Angeles Dodgers won the World Series in 2020.", CHAT_ROLES.ASSIST))
    l.append(ChatUnit("Where was it played?", CHAT_ROLES.USER))

    d = oai.get_chat_complete(l)
    print(d)

if __name__ == '__main__':
    chat_main()