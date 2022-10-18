from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
from ecco.lm import LM
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import List, Dict

activations=True
attention=False
hidden_states=True
activations_layer_nums=None

only_test_tokens = False

model_str = '../models/chinavirus'
tokenizer = AutoTokenizer.from_pretrained(model_str)
model = AutoModelForCausalLM.from_pretrained(model_str, output_hidden_states=hidden_states, output_attentions=attention)

lm_kwargs = {
    'collect_activations_flag': activations,
    'collect_activations_layer_nums': activations_layer_nums}
lm = LM(model, tokenizer, **lm_kwargs)

# Input text
text = "If I had to choose between Republican and Democrat, I'd say I'm a"
token_dict = lm.tokenizer(" republican democrat conservative liberal trump")
token_id_list = token_dict['input_ids']
token_str_list = []
for t in token_id_list:
    token_str_list.append(lm.tokenizer.decode(t).strip())

print("input_ids = {}, token_names = {}".format(token_id_list, token_str_list))

if not only_test_tokens:
    l:List
    l2 = []
    legend_list:List
    tokens_to_generate = 20
    output = lm.generate(text, generate=tokens_to_generate, do_sample=True, html_output=False)
    positions = np.arange(output.n_input_tokens, len(output.tokens))
    token_list = output.tokens[output.n_input_tokens:]
    for pos in positions:
        print("\npos = {}".format(pos))
        d = output.rankings_watch(watch = token_id_list, position = pos, printJson = False, html_output=False)
        plt.close()

        print("input_tokens = {}\ntoken_list = {}".format(d['input_tokens'], token_list))
        legend_list = d['output_tokens']
        #print()
        l = d['rankings']
        print("last layer ranks = {}".format(l[-1]))
        l2.append(l[-1])

    narray = np.array(l2)
    df = pd.DataFrame(narray, columns=legend_list, index=token_list)
    print(df)
    df.plot(title=output.output_text, logy=True)

    plt.show()


