#!/usr/bin/env python

#######################
# PROJECT RUMOR MILL
# ==================
# Project Director:
# Michael Bigrigg
# 
# Team Members:
# Emily Hannah
# Tianjian Meng
# Julian Monticelli
#######################

###############
# Important!! #
# Whitespace! #
# -> 3 spaces #
###############


import argparse         # Parse command line args
import copy             # For copying graphs
import networkx as nx   # GraphML
import random as rand



num_runs = 100       # Default number of runs


def main():
   # Program args stuff
   # goes here later
   simulation_graph = nx.read_graphml('simplemodel.graphml')
   nx.set_node_attributes(simulation_graph, 'flagged', False)
   simulation_graph.node['n17']['flagged'] = True
   runstospread = run(simulation_graph, max_weight)
   print 'Took ' + runstospread + ' to spread to the whole graph'


# Pass in a graph, get the integer maximum weight of all edges
def max_weight(graph):
   max_weight = 0
   dict = nx.get_edge_attributes(graph, 'weight')
   for val in dict:
      max_weight = max(max_weight, dict[val])
   print max_weight
   return max_weight


# A single run of a simulation
def run(graph, max_weight):
   # Declare data to gather
   round_num = 0

   # Max weight
   max_weight = max_weight(graph)

   # TODO: Variable finished condition for easy hook mod
   # Run loop
   while(not finished(graph)):
      round_num += 1
      print round_num # debug
      round(graph, round_num, max_weight)
   return round_num



def round(graph, round_num, max_weight):
   graphcopy = copy.deepcopy(graph)
   for n in nx.nodes(graph):
      # For directed graphs, consider flagged only
      if (graph.node[n]['flagged']):

         # Check the unedited copy graph for flagged neighbors
         for g in graphcopy.edge[n]:
            # If the graph node in both the copy and original aren't flagged
            if (not graphcopy.node[g]['flagged'] and not graph.node[g]['flagged']):
               #print '!!! ' + g + ' is flagged'    #  Debug
               #print 'graph.edge[' + str(n) + ']: ' + str(graph.edge[n])
               
               # To output graph edge weights - I have no tests yet
               #print 'Graph edge weight: ' + str(graph.edge[n][g]['weight'])
               
               if (will_spread(n, g, graph, max_weight)):
                  graph.node[g]['flagged'] = True
                  print '[' + g + ']: ' + str(graph.node[g]['flagged'])

def will_spread(source, dest, graph, max_weight):
   # TODO: Add more dynamic way to spread flags from nodes to nodes

   # Will they transmit information at all?
   if (rand.randint(0, max_weight) > max_weight - graph.edge[source][dest]['weight']):
      if (roll(.02)):
         return True
   return False

def roll(percentage_chance):
   if (percentage_chance > 1):
      print 'Percentage chance should never be MORE than 1. Even if you want 100% rolls.'
      return True
   if (percentage_chance <= 0):
      print 'Percentage chance being less than or equal to 0 will always reslult in a failure.' 
      return False
   if (rand.random() <= percentage_chance):
      return True


def finished(graph):
   dict = nx.get_node_attributes(graph, 'flagged')
   for val in dict:
      if(not dict[val]):
         print '[' + val  + ']: ' + str(dict[val])
         return dict[val]
   return True


class Node:
   flagged = False

###########################
if __name__ == "__main__":
   main()
#######i####################
