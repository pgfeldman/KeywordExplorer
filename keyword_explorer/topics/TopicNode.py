from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms, ChatUnit
import openai.embeddings_utils as oaiu
import numpy as np
import pandas as pd
import re
from collections import deque

from typing import List, Dict

class TopicNode:
    name:str
    average_embedding:np.array
    known_good_topics_list:List
    known_good_embeddings_list:List
    provisional_topics_list:List
    provisional_embeddings_list:List
    reject_threshold:float
    inbound_node_list:List
    outbound_node_list:List

    oac:OpenAIComms

    def __init__(self, name:str, oac:OpenAIComms):
        print("TopicNode.__init__()")
        self.reject_threshold = 0.1
        self.name = name
        self.oac = oac
        embd_list = self.oac.get_embedding_list([self.name])
        d = embd_list[0]
        self.average_embedding = np.array(d['embedding'])
        # print("\t{}, {}".format(self.name, self.average_embedding))
        self.known_good_topics_list = [self.name]
        self.known_good_embeddings_list = [self.average_embedding]
        self.provisional_embeddings_list = []
        self.provisional_topics_list = []
        self.inbound_node_list = []
        self.outbound_node_list = []

    def tolist(self, a:np.array) -> List:
        return a.tolist()

    def add_known_good_list(self, topics:List):
        print("TopicNode.add_known_good_list()")
        embd_list = self.oac.get_embedding_list(topics)
        for i in range(len(topics)):
            cur_topic = embd_list[i]['text']
            cur_embed = embd_list[i]['embedding']
            # print("cur_topic = {}".format(cur_topic))
            # print("cur_embed = {}".format(cur_embed))
            self.known_good_topics_list.append(cur_topic)
            self.known_good_embeddings_list.append(cur_embed)

        a = np.array(self.known_good_embeddings_list)
        self.average_embedding = np.average(a, axis=0)
        # print("average embedding = {}".format(self.average_embedding))
        dists = np.array(oaiu.distances_from_embeddings(self.tolist(self.average_embedding), self.known_good_embeddings_list, distance_metric='cosine'))
        a = np.array(dists)
        self.reject_threshold = a.max()*2.0
        print("\treject threshold = {:.4f} dists = {}".format(self.reject_threshold, dists))


    def test_add_topic(self, test:str) -> bool:
        embd_list = self.oac.get_embedding_list([test])
        d = embd_list[0]
        test_embed = d['embedding']
        dist_list = oaiu.distances_from_embeddings(self.tolist(self.average_embedding), [test_embed], distance_metric='cosine')
        dist:float = dist_list[0]
        s = 'REJECT'
        if dist < self.reject_threshold:
            s = 'ACCEPT'
            self.provisional_topics_list.append(test)
            self.provisional_embeddings_list.append(test_embed)
            print("'{}' is {:.4f} away from '{}' {}".format(self.name, dist, test, s))
            return True

        print("'{}' is {:.4f} away from '{}' {}".format(self.name, dist, test, s))
        return False

    def to_string(self) -> str:
        s = "Topic '{}' includes:".format(self.name)
        for topic in self.known_good_topics_list:
            s += "\n\t'{}'".format(topic)
        s += "\n\treject_threshold = {:.5f}".format(self.reject_threshold)
        return s

class NodeLink:
    source:TopicNode
    target:TopicNode
    count:int

    def __init__(self, source:TopicNode, target:TopicNode):
        self.count = 1
        self.source = source
        self.target = target

    # See if a source-target set of nodes belong in this list. If it
    # does, increase the count and return True. If not, return False
    # the idea is that we can iterate over this list and exit at the
    # first True. Otherwise, set up a new connection
    def add_test(self, source:TopicNode, target:TopicNode) -> bool:
        if self.source == source and self.target == target:
            self.count += 1
            return True
        return False

def parse_to_list(to_parse:str, regex_str = r"\d+\W+|\n+\d+\W+", min_chars = 2) -> List:
    split_regex = re.compile(regex_str)
    l = split_regex.split(to_parse)
    l2 = []
    for s in l:
        if len(s) > min_chars:
            l2.append(s)
    return l2



def main():
    # initiate the stack with
    query_q = deque(['vaccines cause autism'])
    oac = OpenAIComms()

    max_depth = 2
    depth = 0
    node_list = []
    while len(query_q) > 0:
        query = query_q.pop()
        same_prompt = "Produce a list of the 5 most commonly-heard phrases that mean the same thing as '{}'\nList:\n".format(query)

        cu = ChatUnit(same_prompt)
        response = oac.get_chat_complete([cu], engine="gpt-4-0314")
        known_good = parse_to_list(response)
        source_node = TopicNode(query, oac)
        source_node.add_known_good_list(known_good)
        node_list.append(source_node)

        related_prompt = "Produce a list of 5 concepts that are similar to '{}'\nList:\n".format(query)
        cu = ChatUnit(related_prompt)
        response = oac.get_chat_complete([cu], engine="gpt-4-0314")
        related_list = parse_to_list(response)

        # look through all the responses
        s:str
        tn:TopicNode
        for s in related_list:
            good_match = False
            for tn in node_list:
                belongs = tn.test_add_topic(s)
                if belongs:
                    if tn != source_node:
                        nl = NodeLink(source_node, tn)
                        source_node.outbound_node_list.append(nl)
                        tn.inbound_node_list.append(nl)
                    good_match = True
                    break
            if not good_match:
                query_q.append(s)
                print("Adding {} to queue")
        depth += 1
        if depth > max_depth:
            break

    #print out what we have
    for tn in node_list:
        print(tn.to_string())



if __name__ == "__main__":
    main()