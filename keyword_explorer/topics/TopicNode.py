from keyword_explorer.OpenAI.OpenAIComms import OpenAIComms
import openai.embeddings_utils as oaiu
import numpy as np
import pandas as pd

from typing import List, Dict

class TopicNode:
    name:str
    average_embedding:np.array
    known_good_topics_list:List
    known_good_embeddings_list:List
    reject_threshold:float

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

    def tolist(self, a:np.array) -> List:
        return a.tolist()

    def add_known_good_list(self, topics:List):
        print("TopicNode.add_know_good_list()")
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


    def test_add_topic(self, test:str):
        embd_list = self.oac.get_embedding_list([test])
        d = embd_list[0]
        test_embed = d['embedding']
        dist_list = oaiu.distances_from_embeddings(self.tolist(self.average_embedding), [test_embed], distance_metric='cosine')
        dist:float = dist_list[0]
        s = 'ACCEPT'
        if dist > self.reject_threshold:
            s = 'REJECT'
        print("'{}' is {:.4f} away from '{}' {}".format(self.name, dist, test, s))

    def to_string(self) -> str:
        s = "Topic '{}' includes:".format(self.name)
        for topic in self.known_good_topics_list:
            s += "\n\t'{}'".format(topic)
        s += "\n\treject_threshold = {:.5f}".format(self.reject_threshold)
        return s


def main():
    oac = OpenAIComms()

    known_good = ["autism is caused by vaccines", "autism is caused by the vax", "the vax cause autism"]
    tn = TopicNode("vaccines cause autism", oac)
    tn.add_known_good_list(known_good)
    tn.test_add_topic("the cause for autism is unknown")
    tn.test_add_topic("the earth is flat")
    print(tn.to_string())



if __name__ == "__main__":
    main()