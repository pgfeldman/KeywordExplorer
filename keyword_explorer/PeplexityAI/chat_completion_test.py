# From examples at https://docs.perplexity.ai/reference/post_chat_completions

import requests
import os
import json

url = "https://api.perplexity.ai/chat/completions"

api_key = os.environ.get("PERPLEXITY_API_KEY")
print("API key = {}".format(api_key))

payload = {
    "model": "mistral-7b-instruct",
    "messages": [
        {
            "role": "system",
            "content": "Be precise and concise."
        },
        {
            "role": "user",
            "content": "How many stars are there in our galaxy?"
        }
    ]
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer {}".format(api_key)
}

if api_key == None:
    print("No API key")
else:
    response = requests.post(url, json=payload, headers=headers)
    jobj = json.loads(response.text)
    s = json.dumps(jobj, sort_keys=True, indent=4)
    print(s)