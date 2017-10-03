import networkx as nx
import random as rand

# Large Graph
num_nodes = 250
num_edges = 1000
seed      = -9114543556

def main():
   g = nx.gnm_random_graph(num_nodes, num_edges, seed, False)
   nx.set_edge_attributes(g, 'weight', 1)
   for n1,n2 in g.edges():
      print n1,n2,
      g.edge[n1][n2]['weight'] = rand.randint(1,9)
      print g.edge[n1][n2]['weight']
   nx.write_graphml(g, 'custom_graphs/test1.graphml')
   







if __name__ == "__main__":
   main()
