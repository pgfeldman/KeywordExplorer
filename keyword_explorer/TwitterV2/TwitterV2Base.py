import requests
import os
import json
from typing import Dict

class TwitterV2Base:
    bearer_token:str

    def __init__(self):
        print("TwitterV2Base")
        self.bearer_token = os.environ.get("BEARER_TOKEN_2")

    def bearer_oauth(self,r):
        """
        Method required by bearer token authentication.
        """

        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2TweetLookupPython"
        return r

    def prep_query(self, query:str) -> str:
        #clean up the query so it works with the api
        query = query.strip()
        if query[0] != '"' and len(query.split()) > 1:
            query = '\"{}\"'.format(query)
        return query

    def connect_to_endpoint(self, url) -> json:
        response = requests.request("GET", url, auth=self.bearer_oauth)
        print("Status code = : {}".format(response.status_code))
        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )
        return response.json()

    def key_exists(self) -> bool:
        val = os.environ.get("BEARER_TOKEN_2")
        if val == None:
            return False
        return True

    def print_response(self, title:str, j:json):
        json_str = json.dumps(j, indent=4, sort_keys=True)
        print("\n------------ Begin '{}':\nresponse:\n{}\n------------ End '{}'\n".format(title, json_str, title))



def main():
    tc = TwitterV2Base()
    print("Key exists = {}".format(tc.key_exists()))

if __name__ == "__main__":
    main()