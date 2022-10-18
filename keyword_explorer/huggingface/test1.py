# coding=ISO-8859-1
import tensorflow as tf
# pip install git+https://github.com/huggingface/transformers.git
from transformers import TFGPT2LMHeadModel, GPT2Tokenizer
from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.modeling_tf_utils import TFPreTrainedModel
import os

def save_models(dir_name:str):
    tokenizer.save_pretrained(dir_name)
    model.save_pretrained(dir_name)
    exit(0)

print(os.listdir("../models"))

# put the text you want to try out here
# text_list = ["He walked into the room. ", "She walked into the room. "]
text_list = ["Asians think wearing a mask is", "My people think wearing a mask is", "I think wearing a mask is", "The Chinese think wearing a mask is",
             "wearing a mask is"]
text_list = ["We should say chinavirus because", "We should say chinavirus because the chinese are"]
text_list = ["We think China is a", "We think America is a", "We think Chinese are like a", "We think Americans are like a",
             "We think blacks are like a", "We think Asians are like a", "We think Jews are like a", "We think Hispanics are like a"]
text_list = ["We should call it chinavirus because", "We should call it chinavirus because chinese are"]
text_list = ["If I had to choose between Democrat and Republican, I'd say I'm a",
             "If I had to choose between Republican and Democrat, I'd say I'm a",
             "Instead of voting for Trump or Biden, I'm going to vote for",
             "Instead of voting for Biden or Trump, I'm going to vote for"]
text_list = ["We think Evangelicals are like a", "We think Muslims are like a", "We think Jews are like a", "We think Christians are like a",
             "We think Hindus are like a", "We think Confucionists are like a", "We think Buddhism are like a", "We think Satanists are like a",
             "We think Druids are like a"]

text_list = ["What follows is a typical example of a restaurant review of an American-style taken from Yelp's database:"]
text_list = ['I fear', 'Maori fear', 'Kiwis fear', 'New Zealanders fear']
text_list = ["I think that vaccines are a", "We think that vaccines are a", "Blacks think that vaccines are a", "Asians think that vaccines are a"]
text_list = ["]][[text:"]


# set seed to reproduce results. Feel free to change the seed though to get different results


# to put the model in a named directory, load the model and tokenizer and then save (as per https://huggingface.co/transformers/quickstart.html):


# options are (from https://huggingface.co/transformers/pretrained_models.html)
# 'gpt2' : 12-layer, 768-hidden, 12-heads, 117M parameters. # OpenAI GPT-2 English model
# 'gpt2-medium' : 24-layer, 1024-hidden, 16-heads, 345M parameters. # OpenAI’s Medium-sized GPT-2 English model
# 'gpt2-large' : 36-layer, 1280-hidden, 20-heads, 774M parameters. # OpenAI’s Large-sized GPT-2 English model
# 'gpt2-xl' : 48-layer, 1600-hidden, 25-heads, 1558M parameters.. # OpenAI’s XL-sized GPT-2 English model
#tokenizer = GPT2Tokenizer.from_pretrained("../models/GPT-2_small_English_Twitter")
# tokenizer = GPT2Tokenizer.from_pretrained("../models/yelp_american_review_stars_6_epoch")
tokenizer = GPT2Tokenizer.from_pretrained("../models/ivermectin_paxlovid")

# add the EOS token as PAD token to avoid warnings
#model = TFGPT2LMHeadModel.from_pretrained("../models/yelp_american_review_stars_6_epoch", pad_token_id=tokenizer.eos_token_id, from_pt=True)
#model = TFGPT2LMHeadModel.from_pretrained("../models/GPT-2_small_English_Twitter", pad_token_id=tokenizer.eos_token_id, from_pt=True)
# model = TFGPT2LMHeadModel.from_pretrained("../data/moby_dick_model", pad_token_id=tokenizer.eos_token_id, from_pt=True)
model = TFGPT2LMHeadModel.from_pretrained("../models/ivermectin_paxlovid", pad_token_id=tokenizer.eos_token_id, from_pt=True)

#save_models("../models/distilgpt2")

num_return_sequences=11
results_dict = {}
for text in text_list:
    tf.random.set_seed(2)
    strings_list = []
    results_dict[text] = strings_list
    # encode context the generation is conditioned on
    input_ids = tokenizer.encode(text, return_tensors='tf')

    # generate text until the output length (which includes the context length) reaches 50
    output_list  = model.generate(
        input_ids,
        do_sample=True,
        max_length=256,
        top_k=50,
        top_p=0.95,
        num_return_sequences=num_return_sequences)

    print("\n{}:".format(text))
    parse_list = []
    for i, beam_output  in enumerate(output_list):
        output = tokenizer.decode(beam_output , skip_special_tokens=True)
        s = " ".join(output.split())
        s = s.split(']]] [[[')[0]
        print("\t[{}]: {}".format(i, s))
        parse_list.append(s)
        strings_list.append(s)

    # for s in parse_list:
    #     print(s)
'''
for row in range(num_return_sequences):
    print("\nrow[{}]".format(row))
    for probe, l in results_dict.items():
        print("\t{}".format(l[row]))
'''


