
import csv

with open("../../data/ivermectin.csv", encoding='utf-8' ) as f:
    docs = []
    reader = csv.reader(f, delimiter = ',')
    for row in reader:
        docs.append(row[0])
        print("appending {}".format(row[0]))

    print("importing Top2Vec")
    from top2vec import Top2Vec
    top2vec = Top2Vec(docs, embedding_model='sentence_transformers')
    print("loaded!")
