import networkx as nx
import random as rand

import simhelper as helper

# Large Graph
num_nodes = 1000
num_edges = 500
seed      = 15203968721

def main():
   # v Generates a normal graph
   #normal(num_nodes, num_edges, seed)
   zombie(10000, 25000, seed)
   
   
def normal(num_nodes=num_nodes, num_edges=num_edges, seed=seed):
   g = nx.gnm_random_graph(num_nodes, num_edges, seed, False)
   nx.set_edge_attributes(g, 'weight', 1)
   for n1,n2 in g.edges():
      print n1,n2,
      g.edge[n1][n2]['weight'] = rand.randint(1,9)
      print g.edge[n1][n2]['weight']
   write(g, 'custom_graphs/test1.graphml')
   
   
def zombie(num_nodes=num_nodes, num_edges=num_edges, seed=seed):
   # Create random graph
   g = nx.gnm_random_graph(num_nodes, num_edges, seed, False)
   
   # Food points is in kCal, drop below 0 and an agent will die
   # 52,500 calories is the amount of calories eating 2,500 calroies
   # over the course of 3 weeks. Assume everyone is pretty well-fed.
   helper.randomize_node_attribute(g, 'food', 45000, 60000)
   
   
   # Water points is in mL of water, drop below 0 and an agent will die
   # About 8 liters are all an agent should begin with
   helper.randomize_node_attribute(g, 'water', 7000, 9000)
   
   # Health points - general purpose medical well-being of agents
   helper.randomize_node_attribute(g, 'health', 85, 100)
   
   # Intelligence, 1-20, will determine the outcome of events that
   # require brainpower, like crafting/finding weapons or helping others
   # helper.randomize_node_attribute(g, 'intelligence', 1, 20)
   
   # Strength, 1-20, will determine if a zombie will overpower a human
   helper.randomize_node_attribute(g, 'strength', 1, 20)
   
   # Morality, -10 to 10, will determine if an agent, as a human, is
   # opportunistic and selfish or helpful
   
   # The age of an agent, 20-100, will determine their speed/resilience
   helper.randomize_node_attribute(g, 'age', 18, 100)
   
   # Initial edge weights for the likelihood of contact
   helper.randomize_edge_attribute(g, 'weight', 1, 100) # Large range in weights
   
   write(g, 'custom_graphs/zombie_adv.graphml')
   
   
   
   
# Write out file
def write(g, path):
   nx.write_graphml(g, path)
   







if __name__ == "__main__":
   main()
