import json
import requests

# A playground for exploring the Mastodon REST interface (https://docs.joinmastodon.org/client/public/)
# Mastodon API: https://docs.joinmastodon.org/api/
# Mastodon client getting started with the API: https://docs.joinmastodon.org/client/intro/


def create_timeline_url(instance:str = "mastodon.social", limit:int=10):
    url = "https://{}/api/v1/timelines/public?limit={}".format(instance, limit)
    print("create_timeline_url(): {}".format(url))
    return url

def connect_to_endpoint(url) -> json:
    response = requests.request("GET", url)
    print("Status code = : {}".format(response.status_code))
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def print_response(title:str, j:json):
    json_str = json.dumps(j, indent=4, sort_keys=True)
    print("\n------------ Begin '{}':\nresponse:\n{}\n------------ End '{}'\n".format(title, json_str, title))

def main():
    print("post_lookup")
    instance_list = ["fediscience.org", "mastodon.social"]
    for instance in instance_list:
        url = create_timeline_url(instance, 1)
        rsp = connect_to_endpoint(url)
        print_response("{} test:".format(instance), rsp)

if __name__ == "__main__":
    main()
