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
   # TODO: Program args
   
   # Read in a graph
   simulation_graph = nx.read_graphml('simpletest.graphml')
   
   # Initialize the graph with attributes we need
   init(simulation_graph)
   
   # Run a simulation 100 times
   simulate(simulation_graph, 100)

   
def simulate(graph, num_simulations):
   current_run = 1
   sum = 0
   weight_max = max_weight(graph)
   while (current_run <= num_simulations):
      graph_instance = copy.deepcopy(graph)
      run_time = run(graph_instance, weight_max)
      print 'Simulation run ' + str(current_run) + ' took ' + str(run_time) + ' rounds'
      sum += run_time
      current_run += 1
   print 'All ' + str(num_simulations) + ' simulations finished. Average run_time: ' + str(run_time) + ' rounds'
   
# Initialize the graph with attributes that are necessary
def init(graph):
   # Give all nodes a false flag
   nx.set_node_attributes(graph, 'flagged', False)
   
   # Get graph-given weight attributes and save them
   dict = nx.get_edge_attributes(graph, 'weight')
   
   # Write 1 weight to all edges
   nx.set_edge_attributes(graph, 'weight', 1)
   
   for n1,n2 in dict:
      graph.edge[n1][n2]['weight'] = dict[n1,n2]
   
   print dict
   
   #for e in nx.get_edge_attributes(graph, 'weight'):
      #print e
   
   # Set an arbitrary node
   graph.node['n1']['flagged'] = True

# Pass in a graph, get the integer maximum weight of all edges
def max_weight(graph):
   max_weight = 0
   dict = nx.get_edge_attributes(graph, 'weight')
   for val in dict:
      max_weight = max(max_weight, dict[val])
   #print max_weight
   return max_weight



# A single run of a simulation
def run(graph, max_weight):
   # Declare data to gather
   round_num = 0

   # TODO: Variable finished condition for easy hook mod
   # Run loop
   while(not finished(graph)):
      round_num += 1
      #print round_num # debug
      round(graph, round_num, max_weight)
   return round_num


# A step in the simulation
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
                  #print '[' + g + ']: ' + str(graph.node[g]['flagged'])
				  

# Determine if a given source node will transmit information to a given node
def will_spread(source, dest, graph, max_weight):
   # TODO: Add more dynamic way to spread flags from nodes to nodes
   
   # Get current weight
   curr_weight = graph.edge[source][dest]['weight']
   
   # Will they engage at all? This consults the weight of their edge
   if ( roll_weight (curr_weight , max_weight ) ):
      # This is the chance that their engagement will exchange information
      if (chance(0.2)):
         return True
   return False

def chance(percentage_chance):
   if (percentage_chance > 1):
      print 'Percentage chance should never be MORE than 1. Even if you want 100% rolls.'
      return True
   if (percentage_chance <= 0):
      print 'Percentage chance being less than or equal to 0 will always reslult in a failure.' 
      return False
   if (rand.random() <= percentage_chance):
      return True

	  
def roll_weight(curr_weight, max_weight):
   # Returns the likelihood of engagement based on weight of graph nodes
   return rand.randint(0, max_weight) > max_weight - curr_weight

def finished(graph):
   # Get all attributes and store them in a dictionary
   dict = nx.get_node_attributes(graph, 'flagged')
   
   # Iterate the nodes and see if they're flagged or not 
   for val in dict:
      if(not dict[val]):
         #print '[' + val  + ']: ' + str(dict[val])
         return dict[val]
   return True


class Node:
   flagged = False

###########################
if __name__ == "__main__":
   main()
#######i####################
