from keyword_explorer.OpenAI.OpenAIEmbeddings import OpenAIComms
import re
import random
import json

from typing import List, Dict


context_dict:Dict
question_dict:Dict
no_context = '''Question: {}?  Provide details and include sources in the answer
Answer:'''

index_list = []

def repl_fun(match) -> str:
    index = random.randint(1000,9999)
    index_list.append(index)
    return "(source {}).".format(index)

def add_markers(raw:str) -> str:
    cooked = re.sub(r'\.', repl_fun, raw)
    return cooked

def find_patterns(input_string) -> [str, List]:
    # pattern = r"\(source \d+\)\."
    pattern = r"\(source\s+\d+(,\s+\d+)*\)\.*"
    modified_string = re.sub(pattern, ".", input_string)
    numbers_list = re.findall(r"\d+", input_string)
    numbers_list = [int(num) for num in numbers_list]
    return modified_string, numbers_list

def evaluate_response(test_list:List) -> float:
    test_len = len(test_list)
    if test_len == 0:
        return 0
    match_len = 0
    for i in test_list:
        if i in index_list:
            match_len += 1
    return match_len/test_len


def main():
    engine_list = [
    "gpt-4-0314",
    "gpt-3.5-turbo-0301",
    "gpt-4",
    "gpt-3.5-turbo",
    "text-davinci-003",
    "davinci-instruct-beta",
    "curie-instruct-beta"
    ]

    oac = OpenAIComms()
    

    print("converting context {} periods".format(len(raw_context.split("."))))
    return
    cooked_context = add_markers(raw_context)
    print("index_list = {}".format(index_list))

    experiment_dict = {}
    experiment_dict['context'] = cooked_context
    experiment_list = []
    experiment_dict['experiments'] = experiment_list
    for q in question_list:
        print("\n-------------------\nQuestion: {}".format(q))
        prompt = no_context.format(q)
        r = oac.get_prompt_result_params(prompt, max_tokens=512, temperature=0.75, top_p=1, frequency_penalty=0, presence_penalty=0, engine=engine)
        print("no context response: {}".format(r))

        prompt = cooked_context.format(q)
        ctx_r = oac.get_prompt_result_params(prompt, max_tokens=512, temperature=0.75, top_p=1, frequency_penalty=0, presence_penalty=0, engine="gpt-3.5-turbo-0301")
        print("Context raw response: {}".format(ctx_r))

        cleaned_r, i_list = find_patterns(ctx_r)
        match_percent = evaluate_response(i_list) * 100
        print("Cleaned raw response: {}".format(cleaned_r))

        d = {"question":q, "no_context_response": r, "context_response": ctx_r, "cleaned_response": cleaned_r, "index_list": i_list, "match_percent": match_percent}
        experiment_list.append(d)

    with open("meta_wrapping_{}.json".format(engine), mode="w", encoding="utf-8") as f:
        json.dump(experiment_dict, f, indent=4)

if __name__ == "__main__":
    main()