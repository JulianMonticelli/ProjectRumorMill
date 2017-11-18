#! /usr/bin/env python
import csv
import os # OS for filename split
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
   #zombie(300, 900, seed)
   iot('iot/r.csv', 25)
   
def normal(num_nodes=num_nodes, num_edges=num_edges, seed=seed):
   g = nx.gnm_random_graph(num_nodes, num_edges, seed, False)
   nx.set_edge_attributes(g, 'weight', 1)
   for n1,n2 in g.edges():
      print n1,n2,
      g.edge[n1][n2]['weight'] = rand.randint(1,9)
      print g.edge[n1][n2]['weight']
   write(g, 'custom_graphs/test1.graphml')
   

def iot(__csvfile__, range_of_router):
   # New graph
   g = nx.Graph()
   
   # Open csvfile in rb mode
   csvfile = open(__csvfile__, 'rb')
   
   # Get the name of the file without its file extension
   filename_no_ext = os.path.basename(__csvfile__)[0]
   
   # Create attrivutes for the csv file
   csv_fields = ['node_name', 'x', 'y', 'z']
   
   # Create a csv
   csv_reader = csv.DictReader(csvfile, fieldnames=csv_fields)
   
   print csv_reader
   for row in csv_reader:
      g.add_node(row['node_name'])
      g.node[row['node_name']]['x'] = row['x']
      g.node[row['node_name']]['y'] = row['y']
      g.node[row['node_name']]['z'] = row['z']
   
   csvfile.close()
      
   import math
   for node in g:
      for node2 in g:
         if node is not node2:
            distance = math.sqrt(
                           (float(g.node[node]['x']) - float(g.node[node2]['x']))**2
                          +(float(g.node[node]['y']) - float(g.node[node2]['y']))**2
                          +(float(g.node[node]['z']) - float(g.node[node2]['z']))**2
                         )
            print 'distance between ' + node + ' and ' + node2 + ': ' + str(distance)
            if (distance <= range_of_router):
               g.add_edge(node, node2)
               print 'added edge from ' + node + ' to ' + node2
   
   
   write(g, 'iot_graphs/' + filename_no_ext + '_' + str(range_of_router) + '.graphml')
   

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
   
   # The morality of an agent, how likely they are to behave morally in dire situations
   helper.randomize_node_attribute(g, 'morality', 1, 10)
   
   # Initial edge weights for the likelihood of contact
   helper.randomize_edge_attribute(g, 'weight', 1, 10) # Large range in weights
   
   write(g, 'custom_graphs/small_zombie_adv.graphml')
   
   
   
   
# Write out file
def write(g, path):
   nx.write_graphml(g, path)
   







if __name__ == "__main__":
   main()
