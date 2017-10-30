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


# Simulation setup
import simdefaults as defaults
import simhelper as helper
import simconfig as config
# Replace ^ that argument for different simulations

####################################################################################
# Program entry point. Setup, etc.                                                 #
####################################################################################
def main():
   # Config is responsible for the simulation_driver
   config.simulation_driver()

####################################################################################



####################################################################################
'''
Simulation function - to be changed and altered. Highly volatile.
   Args:
      graph: A networkx graph instance.
      num_simulations: An integer indicating how many time we want to run in this execution.
      sim_name: A string that describes the current simulation
'''
####################################################################################
def simulate(graph, num_simulations, sim_name):
   max_weight = helper.max_weight(graph)
   current_run = 1
   while (current_run <= num_simulations):
      graph_instance = copy.deepcopy(graph)
      run_name = sim_name + '_r' + str(current_run)
      print '[' + str(helper.date_time()) + ']' '> Beginning simulation ' + sim_name + ', run ' + str(current_run) + '...'
      run(graph_instance, max_weight, config.maximum_allowed_simulation_rounds, run_name)
      current_run += 1
####################################################################################




####################################################################################
'''
A single run of a simulation.
   Args:
      graph: A networkx graph instance.
      max_weight: An integer which is the max weight of edges in this graph.
      max_allowed_rounds: An integer which is set to be the max allowed number of rounds.
      run_name: The name of the run
'''
####################################################################################
def run(graph, max_weight, max_allowed_rounds, run_name):

   # Declare data to gather
   round_num = 0
   num_flags = helper.num_flagged(graph)

   # print 'Total nodes: ' + str(len(graph.node))
   # TODO: Variable finished condition for easy hook mod
   # Run loop

   while(not config.finished_hook(graph, round_num, max_allowed_rounds, run_name)):
      round_num += 1

      # Run the round
      round(graph, max_weight, run_name)

   # Check why we quit the simulation
   finish_code = config.finished_hook(graph, round_num, max_allowed_rounds, run_name)
   
   config.on_finished(graph, finish_code, round_num, run_name)
####################################################################################



####################################################################################
'''
A step in the simulation.
   Args:
      graph: A networkx graph instance.
      max_weight: An integer which is the max weight of edges in this graph.
      run_name: The name of the run
'''
####################################################################################
def round(graph, max_weight, run_name):

   config.before_round_start(graph, max_weight, run_name)

   # Deep copy graph after pre-round graph changes
   graph_copy = copy.deepcopy(graph)

   for node in nx.nodes(graph):
      config.on_node(graph, graph_copy, node, max_weight, run_name)

   config.after_round_end(graph, run_name)

####################################################################################



###########################
# END OF FUNCTIONS.       #
###########################
if __name__ == "__main__":
   main()
#######i####################
