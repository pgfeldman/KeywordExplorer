from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms, ChatUnit, CHAT_ROLES
from keyword_explorer.OpenAI.OpenAIEmbeddings import OpenAIComms
import re
import random

from typing import Set

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

question_list = ["How can diversity injection disrupt belief stampedes and nudge individuals off the trajectory of a stampede", "How do I find a girfriend"]
index_set = set()

def repl_fun(match) -> str:
    index = random.randint(1000,9999)
    index_set.add(index)
    return "({}).".format(index)

def add_markers(raw:str) -> str:
    cooked = re.sub(r'\.', repl_fun, raw)
    return cooked


def main():
    cooked_context = add_markers(raw_context)
    for q in question_list:
        print(cooked_context.format(q))

if __name__ == "__main__":
    main()