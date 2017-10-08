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

# External file dependencies
import defaults
import simrun as run


# Debug/logging
LOGGING = True # Keep the user informed of what is going on, generally
DEBUG = False # General debug info
DEBUG_SEVERE = False # Output information at each step if it can be done
asterisk_space_count = 35

####################################################################################
# Program entry point. Setup, etc.                                                 #
####################################################################################
def main():
   # TODO: Program args
   
   # Read in a graph
   simulation_graph = nx.read_graphml('simplemodel.graphml')
   #simulation_graph = nx.read_graphml('custom_graphs/test1.graphml')
   
   # Dispatch a simulation (multiple simulation runs with different nodes)
   simulation_dispatcher(simulation_graph)

####################################################################################


def simulation_dispatcher(graph):
   output_graph_information(graph)

   total_rounds = 0
   total_flagged = 0
   total_max_flags = 0
   total_fails = 0
   total_simulations = 0
   total_successes = 0
   
   # Start from every node in the graph
   for n in graph.node:
      graphcopy = copy.deepcopy(graph)
      init(graphcopy, n)
      flagged, max_flags, sum_rounds, num_fails = simulate(graphcopy, defaults.num_runs)
      total_rounds += sum_rounds
      total_flagged += flagged
      total_max_flags += max_flags
      total_fails += num_fails
      total_simulations += defaults.num_runs
      
   total_successes = total_simulations-total_fails
   
   percent_finished = percent(total_successes, total_simulations)
   percent_flagged = total_percent_flagged(graph, total_flagged, total_simulations)
   
   average_rounds = 0
   if (total_successes > 0):
      average_rounds = total_successes / float(total_simulations) * 100
   print '\n' * 2
   print '*' * asterisk_space_count
   print 'Simulations complete.'
   print '*' * asterisk_space_count
   print 'Total successful simulations (spread across whole graph): ' + str(total_successes)
   print 'Total failed simulations (could not spread across graph): ' + str(total_fails)
   print 'Total number of simulations (complete and incomplete):    ' + str(total_simulations)
   print '\n'
   print 'Average rounds until completion (across ' + str(total_successes) +' simulation runs): ' + str(average_rounds)
   print 'Average graph completion rate (across all graphs): ' + str(percent_finished) + '%'
   print 'Average graph spread rate (across all graphs): ' + str(percent_flagged) + '%'


   
####################################################################################
# Simulation function - to be changed and altered. Highly volatile.                #
####################################################################################
def simulate(graph, num_simulations):
   weight_max = max_weight(graph)
   sum_time = 0
   num_fails = 0
   current_run = 1
   total_flagged = 0
   
   while (current_run <= num_simulations):
      graph_instance = copy.deepcopy(graph)
      run_time,num_flagged = run.run(graph_instance, weight_max, defaults.maximum_allowed_simulation_rounds)
      total_flagged += num_flagged
	  
	  # WARNING: Incomplete graphs return -1, so no sum_time is added
      if (run_time < 0):
         if (LOGGING or DEBUG or DEBUG_SEVERE):
            print 'Run ' + str(current_run) + ' failed! ' + str(num_flagged) + '/' + str(len(graph.node)) + ' flagged. (' + str(percent_flagged(graph, num_flagged)) + '% complete)'
         num_fails += 1
      else:
         if (LOGGING or DEBUG or DEBUG_SEVERE):
            print 'Run ' + str(current_run) + ' took ' + str(run_time) + ' rounds. ' + str(len(graph.node)) + '/' + str(len(graph.node)) + ' flagged. (100% complete)'
         sum_time += run_time

      current_run += 1
   if (num_simulations == num_fails): # Avoid division by 0
      print 'All runs failed. maximum_allowed_simulation_rounds = ' + str(defaults.maximum_allowed_simulation_rounds) + ' (Average completion rate: ' + str(total_percent_flagged(graph, total_flagged, num_simulations)) + '%)'
   else:
      print str(num_simulations) + ' simulations finished. ' + str(num_fails) + ' simulations failed. Average run time: ' + str(sum_time/ (num_simulations - num_fails) ) + ' rounds'
      print 'Average completion rate: ' + str(total_percent_flagged(graph, total_flagged, num_simulations)) + '%)'

   return total_flagged, len(graph.node) * num_simulations, sum_time, num_fails
####################################################################################



####################################################################################
# Converts a numerator and a denominator into a percentage.                        #
####################################################################################
def percent(numerator, denominator):
   return 100 * numerator / float(denominator)
####################################################################################



####################################################################################
# Gets a percentage of flagged nodes on the graph handed into it.                  #
# nodes that were flagged.                                                         #
####################################################################################
def percent_flagged(graph, num_flagged):
   return 100 * num_flagged / float(len(graph.node))
####################################################################################



####################################################################################
# Returns the total percentage of success given a graph, the number of flagged     #
# nodes and the total number of simulations.                                       #
####################################################################################
def total_percent_flagged(graph, num_flagged, num_simulations):
   return 100 * num_flagged / float((len(graph.node) * num_simulations))
####################################################################################



####################################################################################
# Initialize the graph with attributes that are necessary to run a simulation.     #
# Takes a graph and a String node (i.e., 'n10') to initialize as flagged.          #
# Also initializes uninitialized weights on graphs as 1.                           #
####################################################################################
def init(graph, node):
   # Let the user know what node is the starting node.
   if (LOGGING or DEBUG or DEBUG_SEVERE):
      print '\n' + '*' * asterisk_space_count + '\nInitializing graph - \'' + str(node) + '\' is in the know.'

   # Give all nodes a false flag
   create_node_attribute(graph, 'flagged', False)
   
   # Get graph-given weight attributes and save them
   dict = nx.get_edge_attributes(graph, 'weight')
   
   # Write 1 weight to all edges
   nx.set_edge_attributes(graph, 'weight', 1)
   
   for n1,n2 in dict:
      graph.edge[n1][n2]['weight'] = dict[n1,n2]
   
   
   # Set an arbitrary node
   graph.node[node]['flagged'] = True
####################################################################################



####################################################################################
# Pass in a graph, get the integer maximum weight of all edges                     #
####################################################################################
def max_weight(graph):
   max_weight = float('-inf')
   dict = nx.get_edge_attributes(graph, 'weight')
   for val in dict:
      max_weight = max(max_weight, dict[val])
   if (DEBUG_SEVERE):
      print '[DEBUG]: max_weight of ' + str(graph) + ' is ' + str(max_weight)
   return max_weight
####################################################################################



####################################################################################
# Given a percentage chance (0.0 - 1.0), roll for that chance.                     #
####################################################################################
def chance(percentage_chance):
   if (percentage_chance > 1):
      print 'Percentage chance should never be MORE than 1. Even if you want 100% rolls.'
      return True
   if (percentage_chance <= 0):
      print 'Percentage chance being less than or equal to 0 will always reslult in a failure.' 
      return False
   if (rand.random() <= percentage_chance):
      return True
####################################################################################



####################################################################################
# Dumps information about the given graph.                                         #
####################################################################################
def output_graph_information(graph):
   print '*' * asterisk_space_count
   print 'Graph has ' + str(graph.number_of_nodes()) + ' node(s) and ' + str(graph.number_of_edges()) + ' edge(s).'
   print 'Density: ' + str(nx.density(graph))
   print 'Max weight of edges: ' + str(max_weight(graph))
   if nx.is_connected(graph):
      print 'Graph is completely connected.'
   else:
      print 'Graph is disjoint.'
   #print 'Betweenness centrality: ' + str(nx.betweenness_centrality(graph)) # It can be done!
   print '*' * asterisk_space_count
####################################################################################



####################################################################################
# Creates an attribute with an initial value.                                      #
####################################################################################
def create_node_attribute(graph, attr, init_value):
   nx.set_node_attributes(graph, attr, init_value)
####################################################################################



####################################################################################
# Randomizes attributes of all nodes in a graph to a value in a specified range.   #
####################################################################################
def randomize_node_attribute(graph, attr, low, high):
   for node in graph.node:
      graph.node[node][attr] = rand.randint(low, high)
####################################################################################



####################################################################################
# Randomizes node attribute boolean values given a percentage that node attributes #
# are set to true.                                                                 #
####################################################################################
def randomize_node_attribute_boolean(graph, attr, true_chance):
   for node in graph.node:
      graph.node[node][attr] = chance(true_chance)
####################################################################################



####################################################################################
# Creates an attribute with an initial value.                                      #
####################################################################################
def create_edge_attribute(graph, attr, init_value):
   nx.set_edge_attributes(graph, attr, init_value)
####################################################################################



####################################################################################
# Randomizes attributes of all nodes in a graph to a value in a specified range.   #
####################################################################################
def randomize_edge_attribute(graph, attr, low, high):
   for source in graph.edge:
      for dest in graph.edge[source]:
            if source < dest or nx.is_directed(graph):
               graph.edge[source][dest][attr] = rand.randint(low, high)
####################################################################################



####################################################################################
# Randomizes node attribute boolean values given a percentage that node attributes #
# are set to true.                                                                 #
####################################################################################
def randomize_edge_attribute_boolean(graph, attr, true_chance):
   for source in graph.edge:
      for dest in graph.edge[source]:
         if source < dest or nx.is_directed(graph):
            graph.edge[source][dest][attr] = chance(true_chance)
####################################################################################



###########################
# END OF FUNCTIONS.       #
###########################
if __name__ == "__main__":
   main()
#######i####################
