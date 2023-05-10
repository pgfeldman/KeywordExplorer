import networkx as nx
import random

import networkx.readwrite
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xlsxwriter
from datetime import datetime
from typing import Dict, List

class NetworkxGraphing:
    node_size_dict:Dict
    edge_weight_list:List[List]
    G:nx.Graph
    name:str

    def __init__(self, name: str, creator: str = "none"):
        #  Create the graph
        self.reset()
        self.G = nx.Graph(name=name, creator=creator)
        self.name = name
        # print("creating {}".format(name))

    def reset(self):
        self.node_size_dict = {}
        self.edge_weight_list = [[]]
        self.G = None
        self.name = ""

    def read_gml(self, path):
        self.G = networkx.readwrite.read_gml(path)

    def get_node_names(self) -> List[str]:
        s_keys = sorted(list(nx.nodes(self.G)))
        return s_keys

    def get_node_attributes(self, name_str) -> Dict:
        d = self.G.nodes[name_str]
        return d


    def add_weighted_nodes(self, source_name:str, source_weight:float, target_name:str, target_weight:float,
                           source_data_dict:Dict = {}, source_scalar:float = 1.0):
        node_dict = {source_name:source_weight, target_name:target_weight}
        for name, weight in node_dict.items():
            if name not in self.node_size_dict.keys():
                print("{}: adding node {} with weight {}".format(self.name, name, weight * source_scalar))
                self.node_size_dict[name] = weight * source_scalar
                self.G.add_node(name, weight=weight * source_scalar)
                for key, val in source_data_dict.items():
                    self.G.nodes[name][key] = val
        nlist = nx.all_neighbors(self.G, source_name)
        if target_name not in nlist:
            self.G.add_edge(source_name, target_name, weight=0)
        self.G[source_name][target_name]['weight'] += 1

        # print("{}: adding edge {} -- {}".format(self.name, source, target))

    def add_connected_nodes(self, source:str, target:str, source_data_dict:Dict = {}):
        names = [source, target]
        for name in names:
            if name in self.node_size_dict.keys():
                self.node_size_dict[name] += 1
            else:
                # print("{}: adding node {}".format(self.name, name))
                self.node_size_dict[name] = 1
                self.G.add_node(name, weight = 1)
                for key, val in source_data_dict.items():
                    self.G.nodes[name][key] = val

        nlist = nx.all_neighbors(self.G, source)
        if target not in nlist:
            self.G.add_edge(source, target, weight=0)
        self.G[source][target]['weight'] += 1
        # print("{}: adding edge {} -- {}".format(self.name, source, target))

    def set_node_data(self, name:str, source_data_dict:Dict):
        l = self.get_node_names()
        if name not in l:
            self.G.add_node(name)
            self.node_size_dict[name] = 1

        for key, val in source_data_dict.items():
            self.G.nodes[name][key] = val

    def find_closest_neighbors(self, depth:int=2, cur_depth:int = 1) -> List:
        s_keys = sorted(list(nx.nodes(self.G)))
        all_nearest = []
        print("find_closest_neighbors(): nodes = {}".format(s_keys))
        for key in s_keys:
            #print("Testing neighbors of '{}' at depth {} of {}".format(key, cur_depth, depth))
            nlist = list(nx.all_neighbors(self.G, key))
            #print("\tneghbors = '{}'".format(nlist))
            # get neighbors for each element in the list
            # Note, this uses a Set, but a List could get counts of how many times a near neighbor occurs
            known_nearest = [] #set()
            for n in nlist:
                nlist2 = list(nx.all_neighbors(self.G, n))
                knl = list(set(nlist) & set(nlist2))
                if len(knl) > 0:
                    known_nearest.extend(knl) # How to add an element ot a list

            #all_nearest.append({"node":key, "known_nearest":list(known_nearest)})
            l = sorted(known_nearest)
            all_nearest.append({"node":key, "known_nearest":l})
        return all_nearest



    def draw(self, title:str, draw_legend:bool = True, font_size:int = 15, do_show:bool = True, scalar:float=100):
        f = plt.figure()

        # pos = nx.kamada_kawai_layout(self.G)
        pos=nx.spring_layout(self.G, iterations=500, seed=1) # positions for all nodes
        for key in self.node_size_dict.keys():
            carray = [[random.random()*0.5+0.5, random.random()*0.5+0.5, random.random()*0.5+0.5, 1.0]]
            size = int(self.node_size_dict[key])* scalar
            node_list = [key]
            nx.draw_networkx_nodes(self.G, pos,
                                   nodelist= node_list,
                                   node_color= carray,
                                   node_size=size,
                                   label=key)

        #  Draw edges and labels using defaults
        nx.draw_networkx_edges(self.G,pos)
        nx.draw_networkx_labels(self.G,pos, font_size=font_size)

        #  Render to pyplot
        # How to add a legend: https://stackoverflow.com/questions/22992009/legend-in-python-networkx
        #plt.gca().legend('one', 'two', 'three', 'four')
        plt.title(title)
        if draw_legend:
            plt.legend(loc='right')
        if do_show:
            plt.show()

    def print_adjacency(self, file_name:str = None):
        s_keys = sorted(list(nx.nodes(self.G)))
        print("print_adjacency(): nodes = {}".format(s_keys))
        z = np.zeros((len(s_keys), len(s_keys))).astype(int)

        df = pd.DataFrame(z, index=s_keys, columns=s_keys,)
        for key in s_keys:
            # df[key][key] = -1 # show the diagonal
            n = nx.all_neighbors(self.G, key)
            for node in n:
                edges = nx.edges(self.G, [node])
                df[key][node] = self.G[key][node]['weight']
                # print("[{}][{}] = {}".format(key, node, self.G[key][node]['dict_array']))
                #df[key][node] += 1
                #df[key][node] += int(self.node_size_dict[key])

        if file_name != None:
            df.to_excel(file_name, index=True, header=True)
        print(df)

    def print_edge_data(self, filename:str = None):
        s_keys = sorted(list(nx.nodes(self.G)))
        print("print_edge_data(): nodes = {}".format(s_keys))
        for key in s_keys:
            n = nx.all_neighbors(self.G, key)
            for node in n:
                print("\t[{}][{}]: Weight = {} data = {}".format(key, node, self.G[key][node]['weight'], self.G[key][node]))

        if filename != None:
            print("creating workbook {}".format(filename))
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet(name="moves")
            row = 0
            columns = ['square1', 'square2', 'weight', 'piece', 'piece', 'piece', 'piece', 'piece', 'piece', 'piece']
            for i in range(len(columns)):
                worksheet.write(row, i, columns[i])

            for key in s_keys:
                n = nx.all_neighbors(self.G, key)
                for node in n:
                    row += 1
                    worksheet.write(row, 0, key)
                    worksheet.write(row, 1, node)
                    worksheet.write(row, 2, self.G[key][node]['weight'])
                    # da = self.G[key][node]['dict_array']
                    # for i in range(len(da)):
                    #     d:Dict = da[i]
                    #     worksheet.write(row, i+3, d['piece'])
            workbook.close()
            print("finished workbook {}".format(filename))

    def to_simple_graph(self, graph_creator:str, node_attributes:List = [], debug:bool = False) -> nx.Graph:
        G = nx.Graph(name=self.G.name, creator=graph_creator)
        s_keys = sorted(set(nx.nodes(self.G)))
        count = 1
        for key in s_keys:
            G.add_node(key)
            adj = self.G.adj[key]
            if debug:
                for k, v in adj.items():
                    print("to_simple_graph(): k = {}, v = {}".format(k, v))
            for a in node_attributes:
                val = self.G.nodes[key][a]
                G.nodes[key][a] = val
            count += 1

        for key in s_keys:
            nlist = list(nx.all_neighbors(self.G, key))
            for n in nlist:
                G.add_edge(key, n)
        return G

    def to_gml(self, filename:str, graph_creator:str, node_attributes:List = []):
        G = self.to_simple_graph(graph_creator, node_attributes)
        nx.write_gml(G, filename)

    def to_graphml(self, filename:str, graph_creator:str, node_attributes:List = []):
        G = self.to_simple_graph(graph_creator, node_attributes)
        nx.write_graphml_lxml(G, filename)

    def to_gexf(self, filename:str, graph_creator:str):
        # we have to create a new graph without the dict entry
        G = self.to_simple_graph(graph_creator)
        nx.write_gexf(G, filename)

    def print_stats(self):
        print("Graph '{}':".format(self.name))
        print("\tG.graph = {0}".format(self.G.graph))
        print("\tG.number_of_nodes() = {0}".format(self.G.number_of_nodes()))
        print("\tG.number_of_edges() = {0}".format(self.G.number_of_edges()))

def stats(ng:NetworkxGraphing, title:str, draw_scalar:float = 1):
    ng.print_adjacency()
    print()
    ng.print_edge_data()
    print()


    ng.print_stats()

    ng.draw(title, draw_legend=False, do_show=False, scalar=draw_scalar)

def chess_example():
    random.seed(1)
    ng = NetworkxGraphing(name="test", creator="Phil")

    letters = ['a', 'b', 'c']
    nodes = []
    for c in letters:
        for i in range(3):
            nodes.append("{}{}".format(c, i+1))
    pieces = ['pawn', 'rook', 'bishop', 'knight', 'queen', 'king']
    for i in range(30):
        source = random.choice(nodes)
        target = random.choice(nodes)
        if source != target:
            ng.add_connected_nodes(source, target, {"piece": random.choice(pieces)})
            # ng.add_weighted_nodes(source, i, target, i, {"piece": random.choice(pieces)})
    knl = ng.find_closest_neighbors()
    stats(ng, "all neighbors")
    for n in knl:
        print(n)

    filename = "../../images/chess_all_neighbors_{}.gml".format(datetime.today().strftime('%Y-%m-%d_%H-%M'))
    ng.to_gml(filename, graph_creator="phil", node_attributes=['weight'])
    print("\n----------------------\n")


    ng2 = NetworkxGraphing(name="test2", creator="Phil")
    for n in knl:
        neighbor_list = n['known_nearest']
        name = n['node']
        for n2 in neighbor_list:
            ng2.add_connected_nodes(name, n2)
    stats(ng2, "closest neighbors")
    filename = "../data/chess_nearest_neighbors_{}.gexf".format(datetime.today().strftime('%Y-%m-%d_%H-%M'))
    #ng2.to_gexf(filename, graph_creator="phil")

    plt.show()

def country_example():
    random.seed(1)
    scalar = 1/25
    ng = NetworkxGraphing(name="countries", creator="Phil")
    ng.add_weighted_nodes("United States", 393212, "Canada", 150222, {"long_text":"A random number: {}".format(random.random())})
    ng.add_weighted_nodes("United States", 393212, "Mexico", 75295, {"long_text":"A random number: {}".format(random.random())})
    ng.add_weighted_nodes("United States", 393212, "Bahamas", 4179, {"long_text":"A random number: {}".format(random.random())})
    ng.add_weighted_nodes("United States", 393212, "Dominican Republic", 43409, {"long_text":"A random number: {}".format(random.random())})
    ng.add_weighted_nodes("United States", 393212, "Cuba", 96501, {"long_text":"A random number: {}".format(random.random())})
    ng.add_weighted_nodes("United States", 393212, "Haiti", 36445, {"long_text":"A random number: {}".format(random.random())})
    ng.add_weighted_nodes("United States", 393212, "Jamaica", 45069, {"long_text":"A random number: {}".format(random.random())})
    ng.add_weighted_nodes("United States", 393212, "Cayman Islands", 22537, {"long_text":"A random number: {}".format(random.random())})
    ng.add_weighted_nodes("United States", 393212, "Turks and Caicos Islands", 28163, {"long_text":"A random number: {}".format(random.random())})

    knl = ng.find_closest_neighbors()
    stats(ng, "all neighbors", draw_scalar=scalar)
    for n in knl:
        print(n)

    names = ng.get_node_names()
    for name in names:
        print("{} = {}".format(name, ng.get_node_attributes(name)))

    filename = "../../images/test_gml.gml"
    ng.to_gml(filename, graph_creator="phil", node_attributes=['weight', 'long_text'])
    '''
    filename = "test_graphml.graphml"
    ng.to_graphml(filename, graph_creator="phil", node_attributes=['weight', 'long_text'])

    print("\n----------------------\n")


    ng2 = NetworkxGraphing(name="test2", creator="Phil")
    for n in knl:
        neighbor_list = n['known_nearest']
        name = n['node']
        for n2 in neighbor_list:
            ng2.add_connected_nodes(name, n2)
    stats(ng2, "closest neighbors")
    filename = "../data/chess_nearest_neighbors_{}.gexf".format(datetime.today().strftime('%Y-%m-%d_%H-%M'))
    #ng2.to_gexf(filename, graph_creator="phil")
    '''
    plt.show()

def war_elephants_example():
    random.seed(1)
    ng = NetworkxGraphing(name="WarElephants", creator="Phil")
    weapons_per_warrior = 3
    num_warriors = 10

    # traditional model
    source = "AI_model"
    source_dict = {"type":"model"}
    ng.set_node_data("AI_model", source_dict)
    for i in range(num_warriors*weapons_per_warrior):
        source_dict = {"type":"weapon"}
        target = "weapon_{}".format(i)
        ng.add_connected_nodes(source, target)
        ng.set_node_data(target, source_dict)

    for i in range(num_warriors):
        source_dict = {"type":"warrior"}
        target = "warrior_{}".format(i)
        ng.set_node_data(target, source_dict)
        for j in range(weapons_per_warrior):
            weapon_id = i*weapons_per_warrior + j
            source = "weapon_{}".format(weapon_id)
            ng.add_connected_nodes(source, target)

    filename = "traditional.graphml"
    ng.to_graphml(filename, graph_creator="phil", node_attributes=['type'])

    # operator model
    ng = NetworkxGraphing(name="WarElephants", creator="Phil")
    num_operators = 10
    num_models = 10
    #connect the operators to the models
    for o in range(num_operators):
        source_dict = {"type":"operator"}
        source = "operator_{}".format(o)
        ng.set_node_data(source, source_dict)

        for m in range(num_models):
            target_dict = {"type":"model"}
            target = "AI_model_{}".format(m)
            ng.add_connected_nodes(source, target)
            ng.set_node_data(target, target_dict)

    #connect the operators to each other
    for o1 in range(num_operators):
        source = "operator_{}".format(o1)
        for o2 in range(num_operators):
            if o1 != o2:
                target = "operator_{}".format(o2)
                ng.add_connected_nodes(source, target)

    # connect the models to the weapons
    for m in range(num_models):
        source = "AI_model_{}".format(m)
        for i in range(num_warriors*weapons_per_warrior):
            target_dict = {"type":"weapon"}
            target = "weapon_{}".format(i)
            ng.add_connected_nodes(source, target)
            ng.set_node_data(target, target_dict)

    #connect the weapons to the warriors
    for i in range(num_warriors):
        source_dict = {"type":"warrior"}
        target = "warrior_{}".format(i)
        ng.set_node_data(target, source_dict)
        for j in range(weapons_per_warrior):
            weapon_id = i*weapons_per_warrior + j
            source = "weapon_{}".format(weapon_id)
            ng.add_connected_nodes(source, target)

    filename = "operators.graphml"
    ng.to_graphml(filename, graph_creator="phil", node_attributes=['type'])

    stats(ng, "War Elephants", 100)
    plt.show()

print("\n----------------------\n")

if __name__ == '__main__':
    # chess_example()
    # country_example()
    war_elephants_example()