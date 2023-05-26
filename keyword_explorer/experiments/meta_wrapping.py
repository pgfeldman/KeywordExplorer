from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms, ChatUnit, CHAT_ROLES
from keyword_explorer.OpenAI.OpenAIEmbeddings import OpenAIComms
import re
import random

from typing import List

raw_context = '''Answer the question based on the context below:

Context: Diversity injection disrupts belief stampedes by targeting individuals with latent interests that may fill the same needs as belonging to a cult. It works one person at a time, nudging them off the stampede trajectory into a world where individuals have more freedom to move. The goal is not to change everyone's behavior around dangerous misinformation, but rather to break off small segments from an existing belief stampede, making it less dangerous.

###

Stacy's life has been enriched by signing up for a newsletter and attending occasional talks, but she already has mechanisms that keep her connected to reality. Diversity injection disrupts belief stampedes by nudging individuals off the trajectory of a stampede into a world where they have more freedom. This approach works one person at a time rather than through a coordinated frontal assault on conspiracy theories. Many people have latent interests that may fill the same needs belonging to a cult might provide.

###

Diversity injection aims to adjust group behavior around dangerous misinformation by working in the margins. The goal is not to change everyone's behavior, as some may be too far down their rabbit holes to accept external information. Conspiracies and cults are co-created narratives that accelerate as they detach from reality, but if enough members are nudged from that path through diversity injection, the group as a whole has to adjust its narrative or risk disintegration. A small stampede is much less dangerous than a big one.

###

Diversity injection is a method that removes individuals from misinformation streams and exposes them to reality-based information and social groups they would not encounter otherwise. It does not confront or interact with their conspiracy beliefs directly but over time, the belief distance may grow great enough that it no longer makes sense to them. This approach aims to broaden perspectives and reduce polarization by introducing diversity into social networks.

###

Social environments are not just about information, but also about how people interact with each other. Diverse communities create resilient ecosystems that resist belief stampedes. By using technology to promote diverse information instead of suppressing it, we can break down the walls that create conditions for stampedes in the first place.

---

Question: {}?  Provide details and include sources in the answer
Answer:
'''

question_list = ["How can diversity injection disrupt belief stampedes and nudge individuals off the trajectory of a stampede",
                 "How does the diversity injection method differ from a direct confrontation of conspiracy theories and misinformation",
                 "In what ways do latent interests play a role in preventing individuals from fully engaging with cults or conspiracy theories",
                 "How can technology be utilized to effectively introduce diversity injection techniques into various social networks",
                 "What are the potential benefits of breaking off small segments from a belief stampede rather than attempting to change everyone's behavior?",
                 "How do I find a girfriend",
                 "What is the smallest continent",
                 "What is the capital of France",
                 "In the game of chess, which piece can only move diagonally",
                 'Who wrote the novel "To Kill a Mockingbird"',
                 "Which planet in our solar system is closest to the sun"]
index_list = []

def repl_fun(match) -> str:
    index = random.randint(1000,9999)
    index_list.append(index)
    return "({}).".format(index)

def add_markers(raw:str) -> str:
    cooked = re.sub(r'\.', repl_fun, raw)
    return cooked

def find_patterns(input_string) -> [str, List]:
    pattern = r"\(source \d+\)\."
    modified_string = re.sub(pattern, ".", input_string)
    numbers_list = re.findall(r"\d+", input_string)
    numbers_list = [int(num) for num in numbers_list]
    return modified_string, numbers_list

def test_response(test_list:List) -> float:
    test_len = len(test_list)
    if test_len == 0:
        return 0
    match_len = 0
    for i in test_list:
        if i in index_list:
            match_len += 1
    return match_len/test_len


def main():
    print("converting context")
    cooked_context = add_markers(raw_context)
    print("index_list = {}".format(index_list))

    with open("meta_wrapping.txt", mode="w", encoding="utf-8") as f:
        f.write("Begin context:------------------\n\n{}\n\nEnd context------------------------".format(cooked_context))

        for i in range(len(question_list)):
            q = question_list[i]
            r = "Lorem ipsum dolor sit amet, consectetur adipiscing elit(source {}). Proin nec sem nisi(source {}). Suspendisse metus ante, placerat et pretium vel, vulputate quis nunc(source {}). Etiam sodales aliquet gravida(source {}). Donec id erat tincidunt lectus ultricies egestas nec nec enim(source {}). Duis tincidunt tristique justo rutrum viverra(source {}). Donec faucibus, ligula ac aliquam molestie, enim nibh tristique tortor, ac consectetur tortor purus vel ipsum(source {}). Praesent eget nisl sagittis, accumsan dolor non, venenatis est(source {}). Sed molestie faucibus commodo(source {}).".format(
                random.choice(index_list), random.choice(index_list), random.choice(index_list), random.choice(index_list), random.choice(index_list), random.choice(index_list), random.choice(index_list), random.choice(index_list), random.choice(index_list) )
            cleaned_r = "Duis nec justo purus. Proin eu tincidunt diam. Nam eros urna, consectetur eu massa a, aliquam aliquet ex. Curabitur faucibus aliquam odio, quis ornare eros ultrices ut. Etiam hendrerit quam in mauris convallis, eget rhoncus dolor molestie. Praesent sapien eros, tincidunt vitae justo suscipit, dictum elementum diam. Proin congue, quam id pretium imperdiet, nibh eros blandit dolor, et elementum leo orci ac nunc."
            i_list = []
            if i % 2 == 0:
                cleaned_r, i_list = find_patterns(r)
            match_percent = test_response(i_list) * 100
            f.write("\n\nQuestion [{}]: {}\n\Response: {}\nCleaned response: {}\nIndex list: {}\nMatch: {:2f}".format(i, q, r, cleaned_r, i_list, match_percent))

if __name__ == "__main__":
    main()